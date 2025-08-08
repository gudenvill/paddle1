#!/bin/bash
# Fix CUDNN for PaddlePaddle on RunPod
# This creates symlinks so PaddlePaddle can find PyTorch's CUDNN libraries

echo "🔧 Fixing CUDNN library paths for PaddlePaddle..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root (or with sudo)"
    exit 1
fi

# Create symlinks for all CUDNN libraries
echo "Creating symlinks for CUDNN libraries..."

# Main CUDNN library
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn.so.8 /usr/local/cuda/lib64/libcudnn.so.8
ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/libcudnn.so.8 /usr/local/cuda/lib64/libcudnn.so

# CUDNN sub-libraries
for lib in libcudnn_ops_infer libcudnn_ops_train libcudnn_cnn_infer libcudnn_cnn_train libcudnn_adv_infer libcudnn_adv_train; do
    if [ -f "/usr/local/lib/python3.10/dist-packages/torch/lib/${lib}.so.8" ]; then
        ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/${lib}.so.8 /usr/local/cuda/lib64/${lib}.so.8
        ln -sf /usr/local/lib/python3.10/dist-packages/torch/lib/${lib}.so.8 /usr/local/cuda/lib64/${lib}.so
        echo "  ✓ Linked ${lib}"
    fi
done

# Update library cache
echo "Updating library cache..."
ldconfig

# Verify CUDNN is now available
echo ""
echo "🔍 Verifying CUDNN installation..."
ls -la /usr/local/cuda/lib64/libcudnn* | head -5

echo ""
echo "✅ CUDNN libraries should now be available to PaddlePaddle!"
echo ""
echo "Now run: ./start_server.sh"