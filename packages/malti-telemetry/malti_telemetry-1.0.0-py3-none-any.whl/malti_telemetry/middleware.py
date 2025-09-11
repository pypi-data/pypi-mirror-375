"""
Malti Starlette Middleware

Generic middleware that works with any Starlette-compatible framework.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Callable, Optional, Union

from starlette.applications import ASGIApp
from starlette.requests import Request
from starlette.routing import Router

from .core import get_telemetry_system

logger = logging.getLogger(__name__)


class MaltiMiddleware:
    """
    Starlette-compatible middleware class for automatic telemetry tracking.

    This middleware works with any Starlette-compatible framework including:
    - Starlette
    - FastAPI
    - Responder
    - APIStar
    - And any other ASGI framework

    Usage:
        app.add_middleware(MaltiMiddleware)
    """

    def __init__(self, app: Any, auto_inject_lifespan: bool = True):
        """
        Initialize the middleware.

        Args:
            app: The ASGI application
            auto_inject_lifespan: Whether to automatically inject lifespan handlers
        """
        self.app = app

        # Auto-inject lifespan handlers for telemetry system management (if enabled)
        if auto_inject_lifespan:
            self._inject_telemetry_lifespan(self.app)

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """ASGI application interface"""
        if scope["type"] != "http":
            # Pass through non-HTTP requests (WebSocket, etc.)
            await self.app(scope, receive, send)
            return

        # Create Starlette Request object directly
        request = self._create_request(scope, receive, send)

        # Process the request
        await self._process_request(request, scope, receive, send)

    def _create_request(self, scope: dict, receive: Callable, send: Callable) -> Any:
        """Create a Starlette Request object"""
        try:
            return Request(scope, receive, send)
        except ImportError:
            # Fallback for when Starlette is not available
            return None

    async def _process_request(self, request: Any, scope: dict, receive: Callable, send: Callable) -> None:
        """Process an HTTP request with telemetry tracking"""
        telemetry_system = get_telemetry_system()

        start_time = time.time()

        # Extract request information
        method = request.method if request else scope.get("method", "GET")
        status = 500  # Default status for error cases
        endpoint = request.url.path if request else scope.get("path", "/")

        try:

            response_status = 200  # Default status

            # Inline send wrapper (required to get response status)
            async def send_wrapper(message: dict) -> None:
                nonlocal response_status
                if message["type"] == "http.response.start":
                    response_status = message.get("status", 200)
                await send(message)

            # Process the request
            await self.app(scope, receive, send_wrapper)

            status = response_status

            # Extract route pattern after request processing
            endpoint = self._extract_route_pattern(request)

            # Extract context information
            context = self._extract_context(request)

            # Extract consumer information
            consumer = self._extract_consumer(request)

            response_time = int((time.time() - start_time) * 1000)

            # Skip recording if in clean mode and status is 401 or 404
            if not telemetry_system.batch_sender.should_ignore_status(status):
                try:
                    # Record the request (thread-safe, non-blocking)
                    telemetry_system.record_request(
                        method=method,
                        endpoint=endpoint,
                        status=status,
                        response_time=response_time,
                        consumer=consumer,
                        context=context,
                    )
                except Exception as e:
                    logger.debug(f"Failed to record telemetry: {e}")

        except Exception:
            try:
                response_time = int((time.time() - start_time) * 1000)
                endpoint = self._extract_route_pattern(request)
                context = self._extract_context(request)
                consumer = self._extract_consumer(request)

                # Record the request (thread-safe, non-blocking)
                telemetry_system.record_request(
                    method=method,
                    endpoint=endpoint,
                    status=status,
                    response_time=response_time,
                    consumer=consumer,
                    context=context,
                )
            except Exception as e:
                logger.debug(f"Failed to record telemetry on error: {e}")

            raise

    def _extract_route_pattern(self, request: Any) -> str:
        """
        Extract route pattern from Starlette request.

        This uses the same approach as FastAPI - the matched route is available
        in the request scope after routing has occurred.

        Returns:
            The route pattern (e.g., "/users/{user_id}") or the actual path if no route is found.
        """
        if not request:
            return "/"

        try:
            # Get the route from the request scope (available after route matching)
            route = request.scope.get("route")
            if route and hasattr(route, "path"):
                return str(route.path)

            # Alternative: try to get from the matched route (FastAPI style)
            if hasattr(request, "route") and hasattr(request.route, "path"):
                return str(request.route.path)

            # If we can't get the route pattern, fall back to the actual path
            # but log a debug message so we know this is happening
            path = str(request.url.path)
            logger.debug(f"Could not extract route pattern for {path}, using actual path")
            return path

        except Exception as e:
            path = str(request.url.path)
            logger.debug(f"Error extracting route pattern: {e}, using actual path")
            return path

    def _extract_context(self, request: Any) -> Optional[str]:
        """Extract context information from request"""
        if not request:
            return None

        # Try to get context from ASGI scope state (if available)
        if hasattr(request, "state") and hasattr(request.state, "malti_context"):
            return str(request.state.malti_context)
        elif "state" in request.scope and "malti_context" in request.scope["state"]:
            return str(request.scope["state"]["malti_context"])
        return None

    def _extract_consumer(self, request: Any) -> str:
        """Extract consumer information from request headers"""
        if not request:
            return "anonymous"

        # Try to get from request state first (FastAPI style)
        if hasattr(request, "state"):
            if hasattr(request.state, "malti_consumer"):
                return str(request.state.malti_consumer)

        # Fall back to headers
        headers = request.headers

        # Check for consumer headers in order of priority
        if "x-consumer-id" in headers:
            return str(headers["x-consumer-id"])
        elif "x-user-id" in headers:  # Fallback for backward compatibility
            return str(headers["x-user-id"])
        elif "consumer-id" in headers:
            return str(headers["consumer-id"])
        elif "user-id" in headers:
            return str(headers["user-id"])

        return "anonymous"

    def _inject_telemetry_lifespan(self, app: Union[ASGIApp, Router]) -> None:
        """
        Automatically inject telemetry lifespan handlers into the application.

        This ensures the telemetry system starts and stops with the application
        without requiring manual lifespan management.
        """
        try:
            router = app
            while not isinstance(router, Router) and hasattr(router, "app"):
                router = router.app
            if not isinstance(router, Router):
                raise TypeError("app must be a Starlette or Router instance")

            lifespan: Optional[Any] = getattr(router, "lifespan_context", None)

            @asynccontextmanager
            async def wrapped_lifespan(app: Any) -> Any:
                # Start telemetry system
                telemetry_system = get_telemetry_system()
                await telemetry_system.start()
                logger.info("Malti telemetry system started via auto-injected lifespan")

                if lifespan is not None:
                    async with lifespan(app):
                        yield
                else:
                    yield

                # Stop telemetry system
                telemetry_system = get_telemetry_system()
                await telemetry_system.stop()
                logger.info("Malti telemetry system stopped via auto-injected lifespan")

            router.lifespan_context = wrapped_lifespan
            logger.debug("Lifespan handlers injected into Starlette application")

        except Exception:
            logger.debug("Could not auto-inject lifespan handlers")

    def _default_extract_route_pattern(self, request: Any) -> str:
        """Default route pattern extraction - just returns the path"""
        if request and hasattr(request, "url"):
            return str(request.url.path)
        return "/"
