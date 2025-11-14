from fastapi import FastAPI, Request, Body
import uvicorn
import logging
import json
import time
import base64
from typing import Any, Dict
from unison_common.logging import configure_logging, log_json
from unison_common.tracing_middleware import TracingMiddleware
from unison_common.tracing import initialize_tracing, instrument_fastapi, instrument_httpx
from collections import defaultdict

app = FastAPI(title="unison-io-vision")
app.add_middleware(TracingMiddleware, service_name="unison-io-vision")

logger = configure_logging("unison-io-vision")

# P0.3: Initialize tracing and instrument FastAPI/httpx
initialize_tracing()
instrument_fastapi(app)
instrument_httpx()

# Simple in-memory metrics
_metrics = defaultdict(int)
_start_time = time.time()

@app.get("/healthz")
@app.get("/health")
def health(request: Request):
    _metrics["/health"] += 1
    event_id = request.headers.get("X-Event-ID")
    log_json(logging.INFO, "health", service="unison-io-vision", event_id=event_id)
    return {"status": "ok", "service": "unison-io-vision"}

@app.get("/metrics")
def metrics():
    """Prometheus text-format metrics."""
    uptime = time.time() - _start_time
    lines = [
        "# HELP unison_io_vision_requests_total Total number of requests by endpoint",
        "# TYPE unison_io_vision_requests_total counter",
    ]
    for k, v in _metrics.items():
        lines.append(f'unison_io_vision_requests_total{{endpoint="{k}"}} {v}')
    lines.extend([
        "",
        "# HELP unison_io_vision_uptime_seconds Service uptime in seconds",
        "# TYPE unison_io_vision_uptime_seconds gauge",
        f"unison_io_vision_uptime_seconds {uptime}",
    ])
    return "\n".join(lines)

@app.get("/readyz")
@app.get("/ready")
def ready(request: Request):
    event_id = request.headers.get("X-Event-ID")
    log_json(logging.INFO, "ready", service="unison-io-vision", event_id=event_id, ready=True)
    return {"ready": True}

@app.post("/vision/capture")
def capture_image(request: Request, body: Dict[str, Any] = Body(...)):
    """
    Image capture stub.
    Returns a placeholder image (1x1 PNG base64 data URL).
    """
    _metrics["/vision/capture"] += 1
    event_id = request.headers.get("X-Event-ID")
    # 1x1 transparent PNG
    png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAqEBgX1Xw3wAAAAASUVORK5CYII="
    image_url = f"data:image/png;base64,{png_b64}"
    log_json(logging.INFO, "vision_capture", service="unison-io-vision", event_id=event_id)
    return {"ok": True, "image_url": image_url, "event_id": event_id}

@app.post("/vision/describe")
def describe_image(request: Request, body: Dict[str, Any] = Body(...)):
    """
    Image description stub.
    Accepts an image_url (data URI) and returns a placeholder description.
    """
    _metrics["/vision/describe"] += 1
    event_id = request.headers.get("X-Event-ID")
    image_url = body.get("image_url")
    if not isinstance(image_url, str) or not image_url.startswith("data:image/"):
        return {"ok": False, "error": "missing or invalid 'image_url' (must be data URI)", "event_id": event_id}
    # MVP: ignore image, return a placeholder description
    description = "This is a placeholder description of the image content."
    log_json(logging.INFO, "vision_describe", service="unison-io-vision", event_id=event_id, description_len=len(description))
    return {"ok": True, "description": description, "event_id": event_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8086)
