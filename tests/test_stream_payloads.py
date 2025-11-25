from fastapi.testclient import TestClient

from src import server  # noqa: E402


def test_capture_includes_metadata():
    client = TestClient(server.app)
    resp = client.post("/vision/capture", json={"person_id": "p1", "session_id": "s1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["person_id"] == "p1"
    assert body["session_id"] == "s1"
    assert "baton" in body


def test_describe_includes_metadata():
    client = TestClient(server.app)
    img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAqEBgX1Xw3wAAAAASUVORK5CYII="
    resp = client.post("/vision/describe", json={"image_url": img, "person_id": "p1", "session_id": "s1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["person_id"] == "p1"
    assert body["session_id"] == "s1"
    assert "baton" in body
