# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

# System deps for psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# ── Runtime ───────────────────────────────────────────────────────────────────
EXPOSE 5000

# Gunicorn: 1 worker, threads for SSE streaming
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "300", "app:app"]
