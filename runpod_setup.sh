#!/bin/bash
# Complete RunPod Setup Script for PaddleOCR WebSocket Server
# Run this after cloning the repo

echo "🚀 Setting up PaddleOCR WebSocket Server..."
echo "=========================================="

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update && apt-get install -y \
    python3-venv \
    libgomp1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libxrender-dev

# Create and activate virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Fix CUDNN libraries
echo "🔧 Fixing CUDNN libraries for GPU support..."
# Create symlinks for CUDNN
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn.so.8 /usr/local/cuda/lib64/libcudnn.so.8
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn.so.8 /usr/local/cuda/lib64/libcudnn.so
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_ops_infer.so.8 /usr/local/cuda/lib64/libcudnn_ops_infer.so.8
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_ops_infer.so.8 /usr/local/cuda/lib64/libcudnn_ops_infer.so
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_ops_train.so.8 /usr/local/cuda/lib64/libcudnn_ops_train.so.8
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_ops_train.so.8 /usr/local/cuda/lib64/libcudnn_ops_train.so
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_cnn_infer.so.8 /usr/local/cuda/lib64/libcudnn_cnn_infer.so.8
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_cnn_infer.so.8 /usr/local/cuda/lib64/libcudnn_cnn_infer.so
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_cnn_train.so.8 /usr/local/cuda/lib64/libcudnn_cnn_train.so.8
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_cnn_train.so.8 /usr/local/cuda/lib64/libcudnn_cnn_train.so
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_adv_infer.so.8 /usr/local/cuda/lib64/libcudnn_adv_infer.so.8
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_adv_infer.so.8 /usr/local/cuda/lib64/libcudnn_adv_infer.so
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_adv_train.so.8 /usr/local/cuda/lib64/libcudnn_adv_train.so.8
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn_adv_train.so.8 /usr/local/cuda/lib64/libcudnn_adv_train.so
ldconfig

echo "✅ CUDNN libraries linked successfully"

# Set environment variables
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/torch/lib:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=0

# Test GPU
echo "🔍 Testing GPU configuration..."
python3 -c "
import paddle
print('  - PaddlePaddle CUDA support:', paddle.is_compiled_with_cuda())
print('  - GPU devices available:', paddle.device.cuda.device_count())
if paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0:
    paddle.device.set_device('gpu:0')
    print('  ✅ GPU test: SUCCESS')
else:
    print('  ⚠️ GPU test: FAILED - will use CPU')
"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "📡 Starting WebSocket OCR Server on port 8765..."
echo "=========================================="

# Start the server
python3 websocket_server.py