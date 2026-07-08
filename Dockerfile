# auraforge API — production image
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY packages/engine/pyproject.toml packages/engine/
COPY packages/engine/auraforge_engine packages/engine/auraforge_engine
COPY data data

RUN pip install --no-cache-dir -e "packages/engine[dev]"

ENV AURAFORGE_SESSION_DIR=/data/sessions
ENV AURAFORGE_EXPORT_DIR=/data/exports
ENV AURAFORGE_CORS_ORIGINS=*
ENV PORT=8787

RUN mkdir -p /data/sessions /data/exports

EXPOSE 8787

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/health')"

CMD ["uvicorn", "auraforge_engine.api:app", "--host", "0.0.0.0", "--port", "8787", "--workers", "1"]
