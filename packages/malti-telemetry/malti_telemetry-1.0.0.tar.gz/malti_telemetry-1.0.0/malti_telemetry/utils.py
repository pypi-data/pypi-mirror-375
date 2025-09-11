"""
Malti Utilities

Utility functions and configuration helpers for the Malti telemetry system.
"""

import logging
import os
from typing import Any, Dict, Optional

from .core import get_telemetry_system

logger = logging.getLogger(__name__)


def get_malti_stats() -> Dict[str, Any]:
    """Get statistics from the global telemetry system instance"""
    telemetry_system = get_telemetry_system()
    return telemetry_system.get_stats()


def configure_malti(
    service_name: Optional[str] = None,
    api_key: Optional[str] = None,
    malti_url: Optional[str] = None,
    node: Optional[str] = None,
    batch_size: Optional[int] = None,
    batch_interval: Optional[float] = None,
    clean_mode: Optional[bool] = None,
) -> None:
    """
    Configure Malti middleware settings.

    This function sets environment variables that the middleware will read.
    Call this before creating your FastAPI app.

    Args:
        service_name: Service name for telemetry
        api_key: Malti API key
        malti_url: Malti server URL
        node: Node identifier
        batch_size: Batch size for sending telemetry
        batch_interval: Batch interval in seconds
        clean_mode: Enable clean mode to ignore 401/404 responses (default: True)
    """
    if service_name:
        os.environ["MALTI_SERVICE_NAME"] = service_name
    if api_key:
        os.environ["MALTI_API_KEY"] = api_key
    if malti_url:
        os.environ["MALTI_URL"] = malti_url
    if node:
        os.environ["MALTI_NODE"] = node
    if batch_size:
        os.environ["MALTI_BATCH_SIZE"] = str(batch_size)
    if batch_interval:
        os.environ["MALTI_BATCH_INTERVAL"] = str(batch_interval)
    if clean_mode is not None:
        os.environ["MALTI_CLEAN_MODE"] = str(clean_mode)

    logger.info("Malti configuration updated")
