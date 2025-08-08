#!/bin/bash
# RunPod WebSocket OCR Server Startup Script
# This script sets up the environment and starts the OCR server with GPU support

echo "🚀 Starting PaddleOCR WebSocket Server on RunPod..."

# Set CUDNN library path for PaddlePaddle to use PyTorch's CUDNN
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/torch/lib:$LD_LIBRARY_PATH
echo "✅ CUDNN library path configured"

# Set CUDA environment variables
export CUDA_VISIBLE_DEVICES=0
echo "✅ CUDA device 0 selected"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Test GPU availability
echo "🔍 Testing GPU configuration..."
python3 -c "
import paddle
print('  - PaddlePaddle CUDA support:', paddle.is_compiled_with_cuda())
print('  - GPU devices available:', paddle.device.cuda.device_count())
paddle.device.set_device('gpu:0')
print('  - GPU device set successfully!')
" || {
    echo "⚠️  GPU test failed, but continuing anyway..."
}

# Kill any existing server processes
pkill -f websocket_server.py 2>/dev/null && echo "✅ Stopped previous server instance"

# Start the WebSocket server
echo ""
echo "📡 Starting WebSocket OCR Server on port 8765..."
echo "=" * 60
python3 websocket_server.py