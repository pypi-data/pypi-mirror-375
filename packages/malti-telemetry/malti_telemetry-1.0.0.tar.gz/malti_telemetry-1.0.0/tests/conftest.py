"""Pytest configuration and fixtures for Malti tests"""

import pytest
import os
from unittest.mock import Mock, AsyncMock

from malti_telemetry.core import TelemetrySystem, BatchSender


@pytest.fixture
def telemetry_system():
    """Create a telemetry system for testing"""
    system = TelemetrySystem()
    return system


@pytest.fixture
def batch_sender():
    """Create a batch sender for testing"""
    sender = BatchSender()
    return sender


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request"""
    request = Mock()
    request.method = "GET"
    request.headers = {}
    request.query_params = {}
    request.state = Mock()
    request.state.malti_context = None
    request.scope = {"route": None}
    request.url = Mock()
    request.url.path = "/api/test"
    return request


@pytest.fixture
def mock_response():
    """Create a mock FastAPI response"""
    response = Mock()
    response.status_code = 200
    return response


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean up environment variables before and after tests"""
    # Save original environment
    original_env = {}
    malti_vars = [
        'MALTI_SERVICE_NAME',
        'MALTI_API_KEY',
        'MALTI_URL',
        'MALTI_NODE',
        'MALTI_BATCH_SIZE',
        'MALTI_BATCH_INTERVAL',
        'MALTI_MAX_RETRIES',
        'MALTI_RETRY_DELAY',
        'MALTI_HTTP_TIMEOUT',
        'MALTI_MAX_KEEPALIVE_CONNECTIONS',
        'MALTI_MAX_CONNECTIONS',
        'MALTI_OVERFLOW_THRESHOLD_PERCENT',
        'MALTI_CLEAN_MODE'
    ]

    for var in malti_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]

    # Clear Malti environment variables
    for var in malti_vars:
        os.environ.pop(var, None)

    yield

    # Restore original environment
    for var, value in original_env.items():
        os.environ[var] = value

    # Clean up any new variables that were set
    for var in malti_vars:
        if var in os.environ and var not in original_env:
            del os.environ[var]
