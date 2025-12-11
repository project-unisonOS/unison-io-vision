# unison-io-vision

Multimodal I/O service for vision: image capture and description stubs. Emits EventEnvelopes to the Orchestrator.

## Status
Optional (dev-mode) — stub vision gateway; used in devstack but can be disabled.

## Run locally

- Python
  - pip install -r requirements.txt
  - cp .env.example .env
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

## Testing
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -c ../constraints.txt -r requirements.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OTEL_SDK_DISABLED=true python -m pytest
```

## Docs

Full docs at https://project-unisonos.github.io
- Repo roles: `unison-docs/dev/unison-repo-roles.md`
- Compatibility: `unison-docs/dev/compatibility-matrix.md`
