# unison-io-vision

Multimodal I/O service for vision: image capture and description stubs. Emits EventEnvelopes to the Orchestrator.

## Run locally

- Python
  - pip install -r requirements.txt
  - python src/server.py
  - Open: http://localhost:8086/health

- Docker
  - docker build -t unison-io-vision:dev .
  - docker run --rm -p 8086:8086 unison-io-vision:dev

## Endpoints

- `GET /health` — liveness
- `GET /ready` — readiness
- `POST /vision/capture` — Image capture stub (returns placeholder image URL)
- `POST /vision/describe` — Image description stub
  - Request: `{ "image_url": "data:image/png;base64,..." }`
  - Returns a text description

## Notes

- Intended for Developer Mode; stub implementations.
- Real vision models will be plugged in later.
