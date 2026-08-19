# -----------------------------------------------------------------------------
# Vaani AI Backend Dockerfile
# Optimized for Render / Railway / Hugging Face Spaces
# -----------------------------------------------------------------------------

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8001

# Install system audio, build tools, and ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY app /app/app
COPY vaani_api.py /app/vaani_api.py
COPY download_models.py /app/download_models.py

# Download AI models into the container image
RUN python download_models.py --yes


# Expose port
EXPOSE 8001

# Run backend production server
CMD ["python", "vaani_api.py"]
