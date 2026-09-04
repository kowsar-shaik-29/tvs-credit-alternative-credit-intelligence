# Production Dockerfile for TVS Credit Alternative Credit Intelligence / NIRNAY API
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    ENVIRONMENT=production

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code and artifacts
COPY app/ ./app/
COPY config/ ./config/
COPY models/ ./models/
COPY main.py .

# Expose default port
EXPOSE 8000

# Cloud Run compatible entrypoint (reads dynamic PORT env var)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
