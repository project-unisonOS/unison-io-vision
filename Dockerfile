FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY constraints.txt ./constraints.txt
COPY unison-common /app/unison-common
COPY unison-io-vision/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -c ./constraints.txt /app/unison-common \
    && pip install --no-cache-dir -c ./constraints.txt -r requirements.txt

COPY unison-io-vision/src/ ./src/
COPY unison-io-vision/tests/ ./tests/

ENV PYTHONPATH=/app/src
EXPOSE 8086
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8086"]
