from time import perf_counter

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest


HTTP_REQUESTS_TOTAL = Counter(
    "aios_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
HTTP_REQUEST_DURATION = Histogram(
    "aios_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "path"],
)
SESSION_CREATED_TOTAL = Counter("aios_session_created_total", "Created Codex sessions")
SESSION_COMPLETED_TOTAL = Counter("aios_session_completed_total", "Completed Codex sessions")
SNAPSHOT_CREATED_TOTAL = Counter("aios_snapshot_created_total", "Created snapshots")
QOS_JOBS_TOTAL = Counter("aios_qos_jobs_total", "QoS jobs created", ["priority_class"])
QOS_JOBS_COMPLETED_TOTAL = Counter("aios_qos_jobs_completed_total", "QoS jobs completed", ["priority_class"])
QOS_QUEUE_DEPTH = Gauge("aios_qos_queue_depth", "Current QoS queue depth")
MCP_TOOL_CALL_TOTAL = Counter("aios_mcp_tool_call_total", "MCP tool calls", ["tool_name", "status"])


def instrument_app(app: FastAPI) -> None:
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start = perf_counter()
        response = await call_next(request)
        path = request.scope.get("route").path if request.scope.get("route") else request.url.path
        HTTP_REQUESTS_TOTAL.labels(request.method, path, str(response.status_code)).inc()
        HTTP_REQUEST_DURATION.labels(request.method, path).observe(perf_counter() - start)
        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
