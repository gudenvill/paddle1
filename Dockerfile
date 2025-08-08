FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies (same as test, plus a few more for production)
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libgomp1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies with working compatible versions  
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY websocket_server.py .
COPY README.md .

# Expose WebSocket port
EXPOSE 8765

# Health check (optional - can be removed if causing issues)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
#   CMD python3 -c "import websockets; import asyncio; asyncio.run(websockets.connect('ws://localhost:8765'))" || exit 1

# Start the WebSocket server
CMD ["python3", "websocket_server.py"]