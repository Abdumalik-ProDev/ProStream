from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import REGISTRY, Counter, Histogram

USER_EVENTS = Counter("prostream_user_events_total", "User events", ["event_type"], registry=REGISTRY)
GRPC_REQUESTS = Counter("prostream_user_grpc_requests_total", "gRPC requests", ["rpc_method"], registry=REGISTRY)
GRPC_LATENCY = Histogram("prostream_user_grpc_request_latency_seconds", "gRPC latency" , ["rpc_method"], registry=REGISTRY)

def instrument_fastapi(app):
    Instrumentator(registry=REGISTRY).instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")