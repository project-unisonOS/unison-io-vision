from fastapi import FastAPI, Request, Body
import uvicorn
import logging
import json
import time
import base64
from typing import Any, Dict
from datetime import datetime, timezone
import os
from unison_common.logging import configure_logging, log_json
from unison_common.tracing_middleware import TracingMiddleware
from unison_common.tracing import initialize_tracing, instrument_fastapi, instrument_httpx
try:
    from unison_common import BatonMiddleware
except Exception:
    BatonMiddleware = None
from collections import defaultdict

APP_NAME = "unison-io-vision"
ORCH_HOST = os.getenv("UNISON_ORCH_HOST", "orchestrator")
ORCH_PORT = os.getenv("UNISON_ORCH_PORT", "8080")
DEFAULT_PERSON_ID = os.getenv("UNISON_DEFAULT_PERSON_ID", "local-user")

app = FastAPI(title=APP_NAME)
app.add_middleware(TracingMiddleware, service_name=APP_NAME)
if BatonMiddleware:
    app.add_middleware(BatonMiddleware)

logger = configure_logging(APP_NAME)

# P0.3: Initialize tracing and instrument FastAPI/httpx
initialize_tracing()
instrument_fastapi(app)
instrument_httpx()

# Simple in-memory metrics
_metrics = defaultdict(int)
_start_time = time.time()


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _http_post_json(host: str, port: str, path: str, payload: Dict[str, Any]) -> tuple[bool, int]:
    try:
        import httpx

        with httpx.Client(timeout=2.0) as client:
            resp = client.post(f"http://{host}:{port}{path}", json=payload, headers={"Accept": "application/json"})
        return resp.status_code in (200, 201, 202), resp.status_code
    except Exception:
        return False, 0


def _emit_caps_report() -> None:
    """Best-effort camera/display report at startup."""
    caps = {
        "camera": {"present": _env_flag("UNISON_HAS_CAMERA", True), "confidence": 0.6},
        "display": {"present": _env_flag("UNISON_HAS_DISPLAY", False), "confidence": 0.6},
        "sign_adapter": {"present": _env_flag("UNISON_HAS_SIGN_ADAPTER", False)},
        "bci_adapter": {"present": _env_flag("UNISON_HAS_BCI_ADAPTER", False)},
    }
    envelope = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": APP_NAME,
        "intent": "caps.report",
        "payload": {"person_id": DEFAULT_PERSON_ID, "caps": caps},
    }
    ok, status = _http_post_json(ORCH_HOST, ORCH_PORT, "/event", envelope)
    log_json(logging.INFO, "caps_report", service=APP_NAME, ok=ok, status=status, caps=caps)


@app.on_event("startup")
def _startup_caps():
    try:
        _emit_caps_report()
    except Exception as exc:  # pragma: no cover - defensive logging
        log_json(logging.WARNING, "caps_report_failed", service=APP_NAME, error=str(exc))

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
    baton = request.headers.get("X-Context-Baton")
    person_id = body.get("person_id")
    session_id = body.get("session_id")
    # 1x1 transparent PNG
    png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAqEBgX1Xw3wAAAAASUVORK5CYII="
    image_url = f"data:image/png;base64,{png_b64}"
    log_json(
        logging.INFO,
        "vision_capture",
        service="unison-io-vision",
        event_id=event_id,
        person_id=person_id,
        session_id=session_id,
    )
    return {
        "ok": True,
        "image_url": image_url,
        "event_id": event_id,
        "person_id": person_id,
        "session_id": session_id,
        "baton": baton,
        "received_at": time.time(),
    }

@app.post("/vision/describe")
def describe_image(request: Request, body: Dict[str, Any] = Body(...)):
    """
    Image description stub.
    Accepts an image_url (data URI) and returns a placeholder description.
    """
    _metrics["/vision/describe"] += 1
    event_id = request.headers.get("X-Event-ID")
    baton = request.headers.get("X-Context-Baton")
    image_url = body.get("image_url")
    person_id = body.get("person_id")
    session_id = body.get("session_id")
    if not isinstance(image_url, str) or not image_url.startswith("data:image/"):
        return {"ok": False, "error": "missing or invalid 'image_url' (must be data URI)", "event_id": event_id}
    # MVP: ignore image, return a placeholder description
    description = "This is a placeholder description of the image content."
    log_json(
        logging.INFO,
        "vision_describe",
        service="unison-io-vision",
        event_id=event_id,
        description_len=len(description),
        person_id=person_id,
        session_id=session_id,
    )
    return {
        "ok": True,
        "description": description,
        "event_id": event_id,
        "person_id": person_id,
        "session_id": session_id,
        "baton": baton,
        "received_at": time.time(),
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8086)
