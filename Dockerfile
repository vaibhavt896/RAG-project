FROM python:3.11-slim

WORKDIR /app

# Reduce memory fragmentation (critical for 512MB free tier)
ENV MALLOC_TRIM_THRESHOLD_=100000
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies based on whether reranker is needed
# On free tier (512MB), set ENABLE_RERANKER=false to skip PyTorch
ARG ENABLE_RERANKER=false
RUN if [ "$ENABLE_RERANKER" = "true" ]; then \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"; \
    else \
    grep -v 'sentence-transformers' requirements.txt > /tmp/requirements-light.txt && \
    pip install --no-cache-dir -r /tmp/requirements-light.txt; \
    fi

COPY . .

EXPOSE 8000

# Single worker to stay within 512MB RAM
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
