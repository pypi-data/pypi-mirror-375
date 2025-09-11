"""Tests for core Malti functionality"""

import os
import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from malti_telemetry.core import TelemetryRecord, TelemetryBuffer, BatchSender, TelemetryCollector, TelemetrySystem


class TestTelemetryRecord:
    """Test TelemetryRecord class"""

    def test_telemetry_record_creation(self):
        """Test creating a telemetry record"""
        record = TelemetryRecord(
            service="test-service",
            method="GET",
            endpoint="/api/test",
            status=200,
            response_time=150,
            consumer="test-consumer"
        )

        assert record.service == "test-service"
        assert record.method == "GET"
        assert record.endpoint == "/api/test"
        assert record.status == 200
        assert record.response_time == 150
        assert record.consumer == "test-consumer"
        assert record.node is None
        assert record.context is None
        assert record.created_at is None

    def test_telemetry_record_to_dict(self):
        """Test converting telemetry record to dictionary"""
        record = TelemetryRecord(
            service="test-service",
            method="GET",
            endpoint="/api/test",
            status=200,
            response_time=150,
            consumer="test-consumer"
        )

        data = record.to_dict()

        assert data["service"] == "test-service"
        assert data["method"] == "GET"
        assert data["endpoint"] == "/api/test"
        assert data["status"] == 200
        assert data["response_time"] == 150
        assert data["consumer"] == "test-consumer"
        assert "created_at" in data

    def test_telemetry_record_with_timestamp(self):
        """Test telemetry record with explicit timestamp"""
        timestamp = datetime.now(timezone.utc)
        record = TelemetryRecord(
            service="test-service",
            method="GET",
            endpoint="/api/test",
            status=200,
            response_time=150,
            consumer="test-consumer",
            created_at=timestamp
        )

        data = record.to_dict()
        assert data["created_at"] == timestamp.isoformat()


class TestTelemetryBuffer:
    """Test TelemetryBuffer class"""

    def test_buffer_creation(self):
        """Test creating a telemetry buffer"""
        buffer = TelemetryBuffer(max_size=100)
        assert buffer.size() == 0
        assert buffer.is_empty()
        assert buffer._buffer.maxlen == 100

    def test_buffer_add_and_get_batch(self):
        """Test adding records and getting batches"""
        buffer = TelemetryBuffer(max_size=10)

        # Add some records
        for i in range(5):
            record = TelemetryRecord(
                service="test",
                method="GET",
                endpoint=f"/api/{i}",
                status=200,
                response_time=100 + i,
                consumer="test"
            )
            buffer.add(record)

        assert buffer.size() == 5
        assert not buffer.is_empty()

        # Get batch
        batch = buffer.get_batch(3)
        assert len(batch) == 3
        assert buffer.size() == 2

        # Get remaining records
        batch = buffer.get_batch(10)
        assert len(batch) == 2
        assert buffer.is_empty()

    def test_buffer_stats(self):
        """Test buffer statistics"""
        buffer = TelemetryBuffer(max_size=10)

        # Add records
        for i in range(3):
            record = TelemetryRecord(
                service="test",
                method="GET",
                endpoint=f"/api/{i}",
                status=200,
                response_time=100,
                consumer="test"
            )
            buffer.add(record)

        stats = buffer.get_stats()
        assert stats["total_added"] == 3
        assert stats["current_size"] == 3
        assert stats["max_size"] == 10

    def test_buffer_maxlen_property(self):
        """Test buffer maxlen property"""
        buffer = TelemetryBuffer(max_size=50)
        assert buffer.maxlen == 50

        buffer_no_max = TelemetryBuffer(max_size=None)
        assert buffer_no_max.maxlen is None

    def test_buffer_update_stats(self):
        """Test buffer update_stats method"""
        buffer = TelemetryBuffer(max_size=10)

        # Initial stats
        stats = buffer.get_stats()
        assert stats["total_sent"] == 0
        assert stats["total_failed"] == 0

        # Update stats
        buffer.update_stats(sent=5, failed=2)

        stats = buffer.get_stats()
        assert stats["total_sent"] == 5
        assert stats["total_failed"] == 2

        # Update again
        buffer.update_stats(sent=3, failed=1)

        stats = buffer.get_stats()
        assert stats["total_sent"] == 8
        assert stats["total_failed"] == 3


class TestBatchSender:
    """Test BatchSender class"""

    def test_batch_sender_creation(self):
        """Test creating a batch sender"""
        sender = BatchSender()
        assert sender.service_name == "default-service"
        assert sender.api_key is None
        assert not sender.running

    def test_should_ignore_status_clean_mode(self):
        """Test status ignoring in clean mode"""
        sender = BatchSender()

        # Clean mode enabled (default)
        assert sender.should_ignore_status(401)
        assert sender.should_ignore_status(404)
        assert not sender.should_ignore_status(200)
        assert not sender.should_ignore_status(500)

    def test_should_ignore_status_no_clean_mode(self):
        """Test status ignoring when clean mode is disabled"""
        import os
        original_value = os.environ.get('MALTI_CLEAN_MODE')
        os.environ['MALTI_CLEAN_MODE'] = 'false'

        try:
            sender = BatchSender()
            assert not sender.should_ignore_status(401)
            assert not sender.should_ignore_status(404)
        finally:
            if original_value is not None:
                os.environ['MALTI_CLEAN_MODE'] = original_value
            elif 'MALTI_CLEAN_MODE' in os.environ:
                del os.environ['MALTI_CLEAN_MODE']


class TestTelemetryCollector:
    """Test TelemetryCollector class"""

    def test_collector_creation(self):
        """Test creating a telemetry collector"""
        sender = BatchSender()
        collector = TelemetryCollector(sender)

        assert collector.batch_sender == sender
        assert collector.service_name == "default-service"
        assert collector.node == "default-node"

    def test_record_request(self):
        """Test recording a request"""
        sender = BatchSender()
        collector = TelemetryCollector(sender)

        collector.record_request(
            method="GET",
            endpoint="/api/test",
            status=200,
            response_time=150,
            consumer="test-consumer",
            context="test-context"
        )

        # Check that record was added to buffer
        assert sender.buffer.size() == 1


class TestTelemetrySystem:
    """Test TelemetrySystem class"""

    def test_system_creation(self):
        """Test creating a telemetry system"""
        system = TelemetrySystem()
        assert isinstance(system.batch_sender, BatchSender)
        assert isinstance(system.collector, TelemetryCollector)

    def test_system_record_request(self):
        """Test recording request through system"""
        system = TelemetrySystem()

        system.record_request(
            method="POST",
            endpoint="/api/users",
            status=201,
            response_time=200,
            consumer="test-user"
        )

        assert system.batch_sender.buffer.size() == 1

    @pytest.mark.asyncio
    async def test_system_start_stop(self):
        """Test starting and stopping the telemetry system"""
        system = TelemetrySystem()

        # Should not fail even without API key
        await system.start()
        assert system.batch_sender.running

        await system.stop()
        assert not system.batch_sender.running


class TestBatchSenderAsync:
    """Test async methods of BatchSender"""

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        """Test starting an already running BatchSender"""
        sender = BatchSender()
        # Set environment variable to avoid HTTP client creation
        os.environ["MALTI_API_KEY"] = "test-key"

        try:
            await sender.start()
            assert sender.running

            # Try to start again - should log warning but not fail
            with patch("malti_telemetry.core.logger") as mock_logger:
                await sender.start()
                mock_logger.warning.assert_called_with("BatchSender is already running")

            await sender.stop()
        finally:
            del os.environ["MALTI_API_KEY"]

    @pytest.mark.asyncio
    async def test_start_with_api_key(self):
        """Test starting BatchSender with API key"""
        os.environ["MALTI_API_KEY"] = "test-key"

        try:
            sender = BatchSender()
            await sender.start()

            assert sender.running
            assert sender._http_client is not None
            assert sender._send_task is not None

            await sender.stop()
            assert not sender.running
            assert sender._http_client is None
        finally:
            del os.environ["MALTI_API_KEY"]

    @pytest.mark.asyncio
    async def test_stop_not_running(self):
        """Test stopping a not running BatchSender"""
        sender = BatchSender()

        # Should not fail
        await sender.stop()
        assert not sender.running

    @pytest.mark.asyncio
    async def test_stop_with_remaining_data(self):
        """Test stopping with remaining data in buffer"""
        os.environ["MALTI_API_KEY"] = "test-key"

        try:
            sender = BatchSender()

            # Add some records
            for i in range(5):
                record = TelemetryRecord(
                    service="test",
                    method="GET",
                    endpoint=f"/api/{i}",
                    status=200,
                    response_time=100,
                    consumer="test"
                )
                sender.add_record(record)

            await sender.start()

            # Mock the send methods to avoid actual HTTP calls
            with patch.object(sender, "_send_remaining_data", new_callable=AsyncMock):
                await sender.stop()
                assert not sender.running

        finally:
            del os.environ["MALTI_API_KEY"]

    @pytest.mark.asyncio
    async def test_overflow_protection(self):
        """Test overflow protection mechanism"""
        os.environ["MALTI_API_KEY"] = "test-key"

        try:
            sender = BatchSender()
            # Set small overflow threshold for testing
            sender.overflow_threshold = 5

            await sender.start()

            # Fill buffer to trigger overflow
            for i in range(10):
                record = TelemetryRecord(
                    service="test",
                    method="GET",
                    endpoint=f"/api/{i}",
                    status=200,
                    response_time=100,
                    consumer="test"
                )
                sender.add_record(record)

            # Should trigger overflow protection
            assert sender.buffer.size() >= sender.overflow_threshold

            await sender.stop()

        finally:
            del os.environ["MALTI_API_KEY"]

    @pytest.mark.asyncio
    async def test_send_batch_success(self):
        """Test successful batch sending"""
        os.environ["MALTI_API_KEY"] = "test-key"

        try:
            sender = BatchSender()
            await sender.start()

            # Create test records
            records = [
                TelemetryRecord(
                    service="test",
                    method="GET",
                    endpoint="/api/test",
                    status=200,
                    response_time=100,
                    consumer="test"
                )
            ]

            # Mock HTTP client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"

            sender._http_client.post = AsyncMock(return_value=mock_response)

            await sender._send_batch(records)

            # Check that stats were updated
            stats = sender.buffer.get_stats()
            assert stats["total_sent"] == 1

            await sender.stop()

        finally:
            del os.environ["MALTI_API_KEY"]

    @pytest.mark.asyncio
    async def test_send_batch_failure(self):
        """Test batch sending failure and retry"""
        os.environ["MALTI_API_KEY"] = "test-key"

        try:
            sender = BatchSender()
            await sender.start()

            # Create test records
            records = [
                TelemetryRecord(
                    service="test",
                    method="GET",
                    endpoint="/api/test",
                    status=500,
                    response_time=100,
                    consumer="test"
                )
            ]

            # Mock HTTP client to always fail
            sender._http_client.post = AsyncMock(side_effect=Exception("Network error"))

            await sender._send_batch(records)

            # Check that failed stats were updated
            stats = sender.buffer.get_stats()
            assert stats["total_failed"] == 1

            await sender.stop()

        finally:
            del os.environ["MALTI_API_KEY"]

    @pytest.mark.asyncio
    async def test_send_batch_http_error(self):
        """Test batch sending with HTTP error response"""
        os.environ["MALTI_API_KEY"] = "test-key"

        try:
            sender = BatchSender()
            await sender.start()

            # Create test records
            records = [
                TelemetryRecord(
                    service="test",
                    method="GET",
                    endpoint="/api/test",
                    status=500,
                    response_time=100,
                    consumer="test"
                )
            ]

            # Mock HTTP client with error response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            sender._http_client.post = AsyncMock(return_value=mock_response)

            # Set max retries to 0 to avoid multiple attempts
            sender.max_retries = 0

            await sender._send_batch(records)

            # Check that failed stats were updated
            stats = sender.buffer.get_stats()
            assert stats["total_failed"] == 1

            await sender.stop()

        finally:
            del os.environ["MALTI_API_KEY"]

    @pytest.mark.asyncio
    async def test_background_sender(self):
        """Test background sender functionality"""
        os.environ["MALTI_API_KEY"] = "test-key"

        try:
            sender = BatchSender()
            # Set short batch interval for testing
            sender.batch_interval = 0.1

            await sender.start()

            # Add some records
            for i in range(3):
                record = TelemetryRecord(
                    service="test",
                    method="GET",
                    endpoint=f"/api/{i}",
                    status=200,
                    response_time=100,
                    consumer="test"
                )
                sender.add_record(record)

            # Wait a bit for background sender to process
            await asyncio.sleep(0.2)

            # Stop sender
            await sender.stop()

            # Background sender should have processed the records
            assert sender.buffer.size() == 0 or sender.buffer.size() < 3

        finally:
            del os.environ["MALTI_API_KEY"]
