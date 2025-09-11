"""Tests for utility functions"""

import os
from unittest.mock import patch

from malti_telemetry import utils
from malti_telemetry.core import get_telemetry_system


class TestConfiguration:
    """Test configuration utilities"""

    def test_configure_malti(self):
        """Test configuring Malti settings"""
        # Save original environment
        original_env = {}
        env_vars = [
            'MALTI_SERVICE_NAME',
            'MALTI_API_KEY',
            'MALTI_URL',
            'MALTI_NODE',
            'MALTI_BATCH_SIZE',
            'MALTI_BATCH_INTERVAL',
            'MALTI_CLEAN_MODE'
        ]

        for var in env_vars:
            if var in os.environ:
                original_env[var] = os.environ[var]

        try:
            # Clear environment
            for var in env_vars:
                os.environ.pop(var, None)

            # Configure Malti
            utils.configure_malti(
                service_name="test-service",
                api_key="test-key",
                malti_url="https://test.example.com",
                node="test-node",
                batch_size=100,
                batch_interval=30.0,
                clean_mode=False
            )

            # Check environment variables were set
            assert os.environ['MALTI_SERVICE_NAME'] == "test-service"
            assert os.environ['MALTI_API_KEY'] == "test-key"
            assert os.environ['MALTI_URL'] == "https://test.example.com"
            assert os.environ['MALTI_NODE'] == "test-node"
            assert os.environ['MALTI_BATCH_SIZE'] == "100"
            assert os.environ['MALTI_BATCH_INTERVAL'] == "30.0"
            assert os.environ['MALTI_CLEAN_MODE'] == "False"

        finally:
            # Restore original environment
            for var in env_vars:
                if var in original_env:
                    os.environ[var] = original_env[var]
                elif var in os.environ:
                    del os.environ[var]

    def test_get_malti_stats(self):
        """Test getting Malti statistics"""
        stats = utils.get_malti_stats()

        # Should return a dictionary
        assert isinstance(stats, dict)
        # Should contain expected keys
        expected_keys = [
            'total_added', 'total_sent', 'total_failed',
            'current_size', 'max_size', 'service_name',
            'node', 'running', 'malti_url', 'clean_mode'
        ]

        for key in expected_keys:
            assert key in stats

    def test_get_telemetry_system_compatibility(self):
        """Test that get_telemetry_system returns a valid system"""
        # Should return a telemetry system instance
        telemetry_system = get_telemetry_system()

        # Should have expected attributes
        assert hasattr(telemetry_system, 'batch_sender')
        assert hasattr(telemetry_system, 'collector')
        assert hasattr(telemetry_system, 'start')
        assert hasattr(telemetry_system, 'stop')
        assert hasattr(telemetry_system, 'record_request')
        assert hasattr(telemetry_system, 'get_stats')
