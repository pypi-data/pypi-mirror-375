__version__ = "1.0.0"

# Core components
from .core import (
    BatchSender,
    TelemetryBuffer,
    TelemetryCollector,
    TelemetryRecord,
    TelemetrySystem,
    get_telemetry_system,
)

# Starlette base integration
from .middleware import (
    MaltiMiddleware,
)

# Utilities
from .utils import (
    configure_malti,
    get_malti_stats,
)

__all__ = [
    # Core classes
    "TelemetryRecord",
    "TelemetryBuffer",
    "BatchSender",
    "TelemetryCollector",
    "TelemetrySystem",
    # Main functions
    "get_telemetry_system",
    # Starlette base integration
    "MaltiMiddleware",
    # Utilities
    "get_malti_stats",
    "configure_malti",
]
