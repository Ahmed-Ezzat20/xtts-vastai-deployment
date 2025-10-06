# XTTSv2 Deployment on Vast.ai with Private Hugging Face Support
# Production-ready Docker container for hosting fine-tuned XTTSv2 models
# Supports both public and private Hugging Face repositories

FROM vastai/pytorch:2.8.0-cuda-12.6.3-py311-24.04

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

# Set working directory
WORKDIR /app

RUN uv sync --locked

#download model


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
CMD ["uv", "run", "app:app", "--host"]
