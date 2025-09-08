from prometheus_client import (
    REGISTRY,
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Response

# HTTP (FastAPI) metrics will be added by Instrumentator (uses REGISTRY)
# Custom metrics you can use across app and gRPC:

# Counts total auth events by type (login/register/refresh/revoke)
AUTH_EVENTS = Counter(
    "prostream_auth_events_total",
    "Total number of auth events by type",
    ["event_type"],
    registry=REGISTRY,
)

# Counts REST requests per path + method (Instrumentator also reports many things,
# but having a concise counter for auth-specific flows is useful)
AUTH_REQUESTS = Counter(
    "prostream_auth_requests_total",
    "Auth service requests processed (labelled by path and method)",
    ["path", "method"],
    registry=REGISTRY,
)

# gRPC metrics
GRPC_REQUESTS = Counter(
    "prostream_grpc_requests_total",
    "Total gRPC requests handled by method",
    ["rpc_method"],
    registry=REGISTRY,
)

GRPC_LATENCY = Histogram(
    "prostream_grpc_request_latency_seconds",
    "gRPC request handling latency (seconds) by method",
    ["rpc_method"],
    registry=REGISTRY,
)

# Generic gauge for long-running values (e.g., DB pool size, queue lag)
DB_ACTIVE_CONNECTIONS = Gauge(
    "prostream_db_active_connections",
    "Number of active DB connections (set by your app if available)",
    registry=REGISTRY,
)

def instrument_fastapi(app):
    """
    Attach prometheus-fastapi-instrumentator to FastAPI app and expose /metrics.
    This will create many standard http metrics (path, status, latency).
    """
    instr = Instrumentator(registry=REGISTRY)
    instr.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

def metrics_response():
    """Return bytes and proper headers for /metrics endpoint if you need to serve manually."""
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
