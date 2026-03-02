FROM python:3.11-slim

WORKDIR /app

# Reduce memory fragmentation (critical for 512MB free tier)
ENV MALLOC_TRIM_THRESHOLD_=100000
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/.cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install PyTorch CPU-only first (saves ~600MB vs full torch)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Download re-ranker model at build time (not runtime)
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

COPY . .

EXPOSE 8000

# Single worker to stay within 512MB RAM
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
