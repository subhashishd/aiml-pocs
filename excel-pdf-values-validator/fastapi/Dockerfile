FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including tesseract for OCR
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p /app/static /app/data /app/models /app/logs

# Pre-download and cache models for offline deployment (edge-optimized)
RUN python -c "import os; os.makedirs('/app/models', exist_ok=True)"
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5', cache_folder='/app/models')" || echo "Embedding model will be downloaded at runtime"
RUN python -c "from transformers import BlipProcessor, BlipForConditionalGeneration; BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base', cache_dir='/app/models'); BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base', cache_dir='/app/models')" || echo "BLIP model will be downloaded at runtime"

# Set environment variables for model caching and Celery
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models
ENV PYTHONPATH=/app
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/1

# Copy application code
COPY app/ ./app/

# Expose ports
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
