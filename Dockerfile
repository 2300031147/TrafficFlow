FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements-server.txt ./
RUN pip install --no-cache-dir -r requirements-server.txt

# Copy application code
COPY server/ ./server/

EXPOSE 8000

CMD ["uvicorn", "server.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
