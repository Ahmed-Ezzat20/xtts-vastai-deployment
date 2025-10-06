# XTTSv2 Deployment on Vast.ai with Private Hugging Face Support
# Production-ready Docker container for hosting fine-tuned XTTSv2 models
# Supports both public and private Hugging Face repositories

FROM vastai/pytorch:2.1.1-cuda-11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies including git-lfs for Hugging Face models
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    git \
    git-lfs \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies including huggingface_hub for private model access
RUN pip install --no-cache-dir \
    xtts-api-server \
    torch==2.1.1+cu118 \
    torchaudio==2.1.1+cu118 \
    huggingface-hub \
    --index-url https://download.pytorch.org/whl/cu118

# Create necessary directories
RUN mkdir -p /app/models /app/speakers /app/outputs /app/scripts

# Copy startup script
COPY scripts/start_server.py /app/scripts/start_server.py
RUN chmod +x /app/scripts/start_server.py

# Copy model files (if available locally)
COPY models/ /app/models/

# Copy speaker samples (if available) 
COPY speakers/ /app/speakers/

# Expose the API port
EXPOSE 8020

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8020/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Set default to Kuwaiti XTTS model (can be overridden)
ENV HUGGINGFACE_MODEL=Genarabia-ai/Kuwaiti_XTTS_Latest

# Hugging Face token should be provided at runtime for private models
# ENV HUGGINGFACE_TOKEN=your_token_here

# Start the server using Python script
CMD ["python", "/app/scripts/start_server.py"]
