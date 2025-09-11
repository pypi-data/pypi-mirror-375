# Malti Python SDK

[![PyPI version](https://badge.fury.io/py/malti-telemetry.svg)](https://pypi.org/project/malti-telemetry/)
[![Python versions](https://img.shields.io/pypi/pyversions/malti-telemetry.svg)](https://pypi.org/project/malti-telemetry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for collecting and sending telemetry data to Malti server using any Starlette-compatible framework.

## Features

- 🚀 **High Performance**: Asynchronous batch processing with connection pooling
- 🔒 **Thread-Safe**: Designed for multi-worker applications
- 🎯 **Clean Mode**: Automatically filters out bot traffic (401/404 responses)
- 🌟 **Multi-Framework**: Works with any Starlette-compatible framework (FastAPI, Starlette, Responder, etc.)
- 📊 **Rich Telemetry**: Collects method, endpoint, status, response time, consumer, and context
- 🔄 **Automatic Batching**: Efficient batching with overflow protection
- ⚡ **Non-Blocking**: Telemetry collection doesn't impact request performance
- 🛡️ **Retry Logic**: Exponential backoff for failed requests
- 🎛️ **Configurable**: Extensive environment variable configuration
- 🔧 **Framework Optimized**: Enhanced integrations for popular frameworks

## Installation

```bash
pip install malti-telemetry
```

## Quick Start

### FastAPI Integration

```python
from fastapi import FastAPI
from malti_telemetry.middleware import MaltiMiddleware

app = FastAPI()

# Add telemetry middleware (route patterns automatically extracted!)
app.add_middleware(MaltiMiddleware)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "name": "John Doe"}

# Recorded as: method=GET, endpoint="/users/{user_id}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
```

### Starlette Integration

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from malti_telemetry.middleware import MaltiMiddleware

app = Starlette()

# Add telemetry middleware (lifespan auto-injected!)
app.add_middleware(Middleware(MaltiMiddleware))

@app.route("/users/{user_id}")
async def get_user(request):
    user_id = request.path_params["user_id"]
    return JSONResponse({"user_id": user_id, "name": "John Doe"})

# Recorded as: method=GET, endpoint="/users/{user_id}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
```

### Responder Integration

```python
from responder import API
from malti_telemetry.middleware import MaltiMiddleware

api = API()

# Add telemetry middleware (generic Starlette middleware works with Responder)
api.add_middleware(MaltiMiddleware)

@api.route("/users/{user_id}")
async def get_user(req, resp, *, user_id):
    resp.media = {"user_id": user_id, "name": "John Doe"}
```

### Generic Starlette Middleware

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from malti_telemetry.middleware import MaltiMiddleware

app = Starlette()

# Add telemetry middleware (works with any Starlette framework)
app.add_middleware(Middleware(MaltiMiddleware))

@app.route("/api/data")
async def get_data(request):
    return JSONResponse({"data": "example"})
```

### Environment Configuration

Set these environment variables before starting your application:

```bash
export MALTI_API_KEY="your-api-key-here"
export MALTI_SERVICE_NAME="my-fastapi-app"
export MALTI_URL="https://your-malti-server.com"
export MALTI_NODE="production-node-1"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MALTI_API_KEY` | *(required)* | Your Malti API key |
| `MALTI_SERVICE_NAME` | `"unknown-service"` | Name of your service |
| `MALTI_URL` | `"http://localhost:8000"` | Malti server URL |
| `MALTI_NODE` | `"unknown-node"` | Node identifier |
| `MALTI_BATCH_SIZE` | `500` | Records per batch |
| `MALTI_BATCH_INTERVAL` | `60.0` | Seconds between batch sends |
| `MALTI_MAX_RETRIES` | `3` | Max retry attempts |
| `MALTI_RETRY_DELAY` | `1.0` | Base retry delay (seconds) |
| `MALTI_HTTP_TIMEOUT` | `30.0` | HTTP request timeout |
| `MALTI_MAX_KEEPALIVE_CONNECTIONS` | `5` | Max keepalive connections |
| `MALTI_MAX_CONNECTIONS` | `10` | Max total connections |
| `MALTI_OVERFLOW_THRESHOLD_PERCENT` | `90.0` | Buffer overflow threshold |
| `MALTI_CLEAN_MODE` | `true` | Ignore 401/404 responses |

### Programmatic Configuration

```python
from malti_telemetry import configure_malti

configure_malti(
    service_name="my-service",
    api_key="your-api-key",
    malti_url="https://api.malti.dev",
    node="prod-web-01",
    batch_size=1000,
    clean_mode=True
)
```

## Advanced Usage

### Framework-Specific Features

#### FastAPI Features

**Route Pattern Extraction**: Automatic conversion of actual paths to route patterns:
- `/users/123` → `/users/{user_id}`
- `/api/v1/posts/456/comments` → `/api/v1/posts/{post_id}/comments`
- Works with nested routes and mount points

**Context Information**: Add context using FastAPI's request state:

```python
from fastapi import Request

@app.route("/users/{user_id}")
async def get_user(request):
    user_id = request.path_params["user_id"]
    if user_id < 1000:
        request.state.context = "legacy"
    else:
        request.state.context = "current"
    return JSONResponse({"user_id": user_id, "name": "John Doe"})
```

#### Starlette Features

**Automatic Lifespan Management**: Telemetry system starts/stops automatically:

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from malti_telemetry.middleware import MaltiMiddleware

app = Starlette()
app.add_middleware(Middleware(MaltiMiddleware))  # Lifespan auto-injected!

# No need for manual lifespan management!
```

**Route Pattern Extraction**: Automatically extracts route patterns from Starlette routing:

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route, Mount
from malti_telemetry.middleware import MaltiMiddleware

app = Starlette()
app.add_middleware(Middleware(MaltiMiddleware))

async def user_handler(request):
    return JSONResponse({"user_id": request.path_params["user_id"]})

async def post_handler(request):
    return JSONResponse({"post_id": request.path_params["post_id"]})

# Works with all Starlette routing patterns
app.routes = [
    Route("/api/v1/users/{user_id}", endpoint=user_handler),
    Mount("/api/v2", routes=[
        Route("/posts/{post_id}", endpoint=post_handler),
    ]),
]

# Automatically recorded as:
# method=GET, endpoint="/api/v1/users/{user_id}"
# method=GET, endpoint="/api/v2/posts/{post_id}"
```

### Consumer Identification

Malti automatically extracts consumer information from headers:

1. `x-consumer-id` header (highest priority)
2. `x-user-id` header (fallback)
3. `consumer-id` header
4. `user-id` header

**Custom Consumer Extraction**: Set consumer information in your framework:

```python
# FastAPI
@app.middleware("http")
async def set_consumer(request: Request, call_next):
    request.state.malti_consumer = "app"
    return await call_next(request)

# Starlette
@app.middleware("http")
async def set_consumer(request, call_next):
    # Add consumer to ASGI scope
    request.scope["state"]["malti_consumer"] = "api"
    response = await call_next(request)
    return response
```

### Manual Telemetry Recording

```python
from malti_telemetry import get_telemetry_system

telemetry = get_telemetry_system()

# Record a custom event
telemetry.record_request(
    method="GET",
    endpoint="/api/custom",
    status=200,
    response_time=150,
    consumer="custom-client",
    context="manual-recording"
)
```

### Statistics and Monitoring

```python
from malti_telemetry import get_malti_stats

stats = get_malti_stats()
print(stats)
# {
#     'total_added': 1250,
#     'total_sent': 1200,
#     'total_failed': 50,
#     'current_size': 50,
#     'max_size': 25000,
#     'service_name': 'my-service',
#     'running': True
# }
```

## Supported Frameworks

Malti Telemetry works with any Starlette-compatible framework:

- **FastAPI**: Enhanced route pattern extraction and request.state integration
- **Starlette**: Base middleware with full functionality and lifespan management
- **Responder**: Works with generic Starlette middleware
- **Any ASGI framework**: Generic middleware for custom implementations

### Architecture

#### Core Components

1. **TelemetryCollector**: Collects HTTP request telemetry data
2. **BatchSender**: Sends batched telemetry data to Malti server
3. **TelemetrySystem**: Combines collector and sender with unified interface
4. **TelemetryBuffer**: Thread-safe buffer for storing records

### Worker Process Model

Each FastAPI/Uvicorn worker process gets its own telemetry system instance:

```
┌─────────────────┐    ┌─────────────────┐
│ Worker Process  │    │ Worker Process  │
│ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │TelemetrySys │ │    │ │TelemetrySys │ │
│ │ ┌─────────┐ │ │    │ │ ┌─────────┐ │ │
│ │ │Buffer   │ │ │    │ │ │Buffer   │ │ │
│ │ └─────────┘ │ │    │ │ └─────────┘ │ │
│ │ ┌─────────┐ │ │    │ │ ┌─────────┐ │ │
│ │ │Sender   │ │ │    │ │ │Sender   │ │ │
│ │ └─────────┘ │ │    │ │ └─────────┘ │ │
│ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘
```

## Development

### Setup

```bash
git clone https://github.com/muzy/malti-telemetry.git
cd python/
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Code Quality

```bash
black malti_telemetry/
isort malti_telemetry/
mypy malti_telemetry/
flake8 malti_telemetry/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
