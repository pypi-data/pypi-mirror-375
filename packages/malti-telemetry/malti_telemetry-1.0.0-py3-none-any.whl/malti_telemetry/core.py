"""
Malti Telemetry System - Core Components

Core classes and functionality for collecting and sending telemetry data.
"""

import asyncio
import logging
import os
import threading
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TelemetryRecord:
    """Represents a single telemetry record"""

    service: str
    method: str
    endpoint: str
    status: int
    response_time: int
    consumer: str
    node: Optional[str] = None
    context: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if data["created_at"] is None:
            data["created_at"] = datetime.now(timezone.utc).isoformat()
        elif isinstance(data["created_at"], datetime):
            data["created_at"] = data["created_at"].isoformat()
        return data


class TelemetryBuffer:
    """Thread-safe buffer for storing telemetry records"""

    def __init__(self, max_size: int = 10000):
        self._buffer = deque(maxlen=max_size)  # type: deque[TelemetryRecord]
        self._lock = threading.RLock()
        self._stats = {"total_added": 0, "total_sent": 0, "total_failed": 0}

    def add(self, record: TelemetryRecord) -> None:
        """Add a telemetry record to the buffer"""
        with self._lock:
            self._buffer.append(record)
            self._stats["total_added"] += 1

    def get_batch(self, batch_size: int) -> List[TelemetryRecord]:
        """Get a batch of records and remove them from buffer"""
        with self._lock:
            batch = []
            for _ in range(min(batch_size, len(self._buffer))):
                if self._buffer:
                    batch.append(self._buffer.popleft())
            return batch

    def size(self) -> int:
        """Get current buffer size"""
        with self._lock:
            return len(self._buffer)

    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        with self._lock:
            return len(self._buffer) == 0

    @property
    def maxlen(self) -> Optional[int]:
        """Get the maximum size of the buffer"""
        with self._lock:
            return self._buffer.maxlen

    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics"""
        with self._lock:
            return {
                **self._stats,
                "current_size": len(self._buffer),
                "max_size": self._buffer.maxlen,
            }

    def update_stats(self, sent: int = 0, failed: int = 0) -> None:
        """Update statistics"""
        with self._lock:
            self._stats["total_sent"] += sent
            self._stats["total_failed"] += failed


class BatchSender:
    """
    Handles batching and sending telemetry data to Malti server.

    This component provides:
    - Automatic batching and sending
    - Retry logic with exponential backoff
    - Graceful shutdown with remaining data flush
    - Environment variable configuration
    """

    def __init__(self) -> None:
        # Configuration from environment variables
        self.service_name = os.getenv("MALTI_SERVICE_NAME", "default-service")
        self.api_key = os.getenv("MALTI_API_KEY")
        self.malti_url = os.getenv("MALTI_URL", "http://localhost:8000")
        self.node = os.getenv("MALTI_NODE", "default-node")

        # Batching configuration
        self.batch_size = int(os.getenv("MALTI_BATCH_SIZE", "500"))
        self.batch_interval = float(os.getenv("MALTI_BATCH_INTERVAL", "60.0"))
        self.max_retries = int(os.getenv("MALTI_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("MALTI_RETRY_DELAY", "1.0"))

        # HTTP client configuration
        self.http_timeout = float(os.getenv("MALTI_HTTP_TIMEOUT", "30.0"))
        max_keepalive = os.getenv("MALTI_MAX_KEEPALIVE_CONNECTIONS", "5")
        self.max_keepalive_connections = int(max_keepalive)
        max_conn = os.getenv("MALTI_MAX_CONNECTIONS", "10")
        self.max_connections = int(max_conn)

        # Overflow protection configuration
        self.overflow_threshold_percent = float(os.getenv("MALTI_OVERFLOW_THRESHOLD_PERCENT", "90.0"))

        # Clean mode configuration - ignore 401 and 404 responses by default
        clean_mode_env = os.getenv("MALTI_CLEAN_MODE", "true")
        self.clean_mode = clean_mode_env.lower() == "true"

        # Internal state
        self.buffer = TelemetryBuffer(max_size=25000)
        self.running = False
        self._send_task: Optional[asyncio.Task] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._send_lock = asyncio.Lock()  # Prevent concurrent sends
        self.ingest_endpoint = f"{self.malti_url}/api/v1/ingest"

        # Overflow protection: send immediately when buffer reaches threshold
        threshold_ratio = self.overflow_threshold_percent / 100.0
        self.overflow_threshold = int(25000 * threshold_ratio)

        # Validate configuration
        if not self.api_key:
            logger.warning("MALTI_API_KEY not set - telemetry will not be sent")

    async def start(self) -> None:
        """Start the middleware background task"""
        if self.running:
            logger.warning("BatchSender is already running")
            return

        self.running = True

        if not self.api_key:
            logger.warning("MALTI_API_KEY not configured - BatchSender will not send data")
            return

        # Create persistent HTTP client with connection pooling
        limits = httpx.Limits(
            max_keepalive_connections=self.max_keepalive_connections,
            max_connections=self.max_connections,
        )
        self._http_client = httpx.AsyncClient(
            timeout=self.http_timeout,
            limits=limits,
        )

        self._send_task = asyncio.create_task(self._background_sender())
        msg = f"BatchSender started for service: {self.service_name} " f"(node: {self.node})"
        logger.info(msg)

    async def stop(self) -> None:
        """Stop the middleware and send any remaining data"""
        if not self.running:
            return

        logger.info("Stopping BatchSender...")
        self.running = False

        if self._send_task:
            self._send_task.cancel()
            try:
                await self._send_task
            except asyncio.CancelledError:
                pass

        # Send any remaining data
        if not self.buffer.is_empty():
            logger.info(f"Sending final batch of {self.buffer.size()} records...")
            await self._send_remaining_data()

        # Close HTTP client
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        logger.info("BatchSender stopped")

    def add_record(self, record: TelemetryRecord) -> None:
        """Add a telemetry record to the buffer"""
        self.buffer.add(record)

        # Overflow protection: send immediately if buffer reaches 90% capacity
        if self.buffer.size() >= self.overflow_threshold:
            buffer_size = self.buffer.size()
            max_size = self.buffer.maxlen
            logger.warning(f"Buffer at {buffer_size}/{max_size} records - " "sending immediately to prevent overflow")
            asyncio.create_task(self._send_overflow_batch())

    async def _send_overflow_batch(self) -> None:
        """Send batches immediately when buffer reaches overflow threshold"""
        async with self._send_lock:
            # Send multiple batches to bring buffer below threshold
            while self.buffer.size() >= self.overflow_threshold:
                batch = self.buffer.get_batch(self.batch_size)
                if batch:
                    await self._send_batch(batch)
                else:
                    break  # No more records to send

    async def _background_sender(self) -> None:
        """Background task that sends all available batches at regular intervals"""
        while self.running:
            try:
                await asyncio.sleep(self.batch_interval)

                # Send ALL available batches in the buffer
                async with self._send_lock:
                    while not self.buffer.is_empty():
                        batch = self.buffer.get_batch(self.batch_size)
                        if batch:
                            await self._send_batch(batch)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background sender: {e}")

    async def _send_remaining_data(self) -> None:
        """Send all remaining data in buffer"""
        async with self._send_lock:
            while not self.buffer.is_empty():
                batch = self.buffer.get_batch(self.batch_size)
                if batch:
                    await self._send_batch(batch)

    async def _send_batch(self, batch: List[TelemetryRecord]) -> None:
        """Send a batch of records to Malti"""
        if not batch or not self.api_key or not self._http_client:
            return

        batch_data = [record.to_dict() for record in batch]

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._http_client.post(
                    self.ingest_endpoint,
                    json={"requests": batch_data},
                    headers={"X-API-Key": self.api_key},
                )

                if response.status_code == 200:
                    self.buffer.update_stats(sent=len(batch))
                    logger.debug(f"Sent batch of {len(batch)} records for {self.service_name}")
                    return
                else:
                    status_code = response.status_code
                    response_text = response.text
                    logger.warning(f"Failed to send batch: {status_code} - {response_text}")
                    # Update failed stats for non-200 responses
                    self.buffer.update_stats(failed=len(batch))
                    return

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to send batch: {e}")

                if attempt < self.max_retries:
                    delay = self.retry_delay * (2**attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                else:
                    max_attempts = self.max_retries + 1
                    logger.error(f"Failed to send batch after {max_attempts} attempts")
                    self.buffer.update_stats(failed=len(batch))

    def should_ignore_status(self, status: int) -> bool:
        """Check if a status code should be ignored in clean mode"""
        if not self.clean_mode:
            return False
        return status in [401, 404]

    def get_stats(self) -> Dict[str, Any]:
        """Get BatchSender statistics"""
        buffer_stats = self.buffer.get_stats()
        return {
            **buffer_stats,
            "service_name": self.service_name,
            "node": self.node,
            "running": self.running,
            "malti_url": self.malti_url,
            "clean_mode": self.clean_mode,
        }


class TelemetryCollector:
    """
    Collects HTTP request telemetry data.

    This component provides:
    - Thread-safe telemetry collection
    - Automatic consumer identification from headers/query params
    - Non-blocking operation
    """

    def __init__(self, batch_sender: BatchSender):
        self.batch_sender = batch_sender
        self.service_name = batch_sender.service_name
        self.node = batch_sender.node

    def record_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        response_time: int,
        consumer: str,
        context: Optional[str] = None,
    ) -> None:
        """
        Record a single HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Request endpoint
            status: HTTP status code
            response_time: Response time in milliseconds
            consumer: Consumer identifier (application/service using the API)
            context: Optional context information for the request
        """
        record = TelemetryRecord(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            status=status,
            response_time=response_time,
            consumer=consumer,
            node=self.node,
            context=context,
            created_at=datetime.now(timezone.utc),
        )

        self.batch_sender.add_record(record)

    def get_stats(self) -> Dict[str, Any]:
        """Get TelemetryCollector statistics"""
        return self.batch_sender.get_stats()


class TelemetrySystem:
    """
    Combines TelemetryCollector and BatchSender.

    This component provides:
    - Unified interface for telemetry collection and sending
    - Lifecycle management (start/stop)
    - Configuration management
    """

    def __init__(self) -> None:
        self.batch_sender = BatchSender()
        self.collector = TelemetryCollector(self.batch_sender)

    async def start(self) -> None:
        """Start the telemetry system"""
        await self.batch_sender.start()
        logger.info("TelemetrySystem started")

    async def stop(self) -> None:
        """Stop the telemetry system"""
        await self.batch_sender.stop()
        logger.info("TelemetrySystem stopped")

    def record_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        response_time: int,
        consumer: str,
        context: Optional[str] = None,
    ) -> None:
        """Record a single HTTP request"""
        self.collector.record_request(method, endpoint, status, response_time, consumer, context)

    def get_stats(self) -> Dict[str, Any]:
        """Get telemetry system statistics"""
        return self.collector.get_stats()


# Global telemetry system instance
_telemetry_system: Optional[TelemetrySystem] = None


def get_telemetry_system() -> TelemetrySystem:
    """
    Get the global telemetry system instance.

    Returns:
        TelemetrySystem: The global telemetry system instance
    """
    global _telemetry_system
    if _telemetry_system is None:
        _telemetry_system = TelemetrySystem()
    return _telemetry_system
