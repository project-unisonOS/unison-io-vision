from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"
    assert j.get("service") == "unison-io-vision"


def test_ready():
    r = client.get("/ready")
    assert r.status_code == 200
    j = r.json()
    assert j.get("ready") is True


def test_vision_capture():
    r = client.post("/vision/capture", json={})
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    image_url = j.get("image_url", "")
    assert image_url.startswith("data:image/png;base64,")


def test_vision_describe_missing_image():
    r = client.post("/vision/describe", json={})
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is False
    assert "image_url" in j.get("error", "")


def test_vision_describe_placeholder():
    r = client.post("/vision/describe", json={"image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAqEBgX1Xw3wAAAAASUVORK5CYII="})
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    assert isinstance(j.get("description"), str)
    assert "placeholder" in j.get("description", "").lower()
