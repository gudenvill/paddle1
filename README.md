# PaddleOCR WebSocket Service

GPU-accelerated OCR service that accepts base64 images via WebSocket and returns text with coordinates.

## Quick Start - Using the Service

### 1. WebSocket Endpoint

The service runs on RunPod. Your WebSocket URL format is:
```
wss://[POD_ID]-8765.proxy.runpod.net/
```

Example: If your pod ID is `mfn9rzbtwrg5c8`, your URL is:
```
wss://mfn9rzbtwrg5c8-8765.proxy.runpod.net/
```

### 2. Sending Images for OCR

Send a JSON message with your base64-encoded image:

```python
import asyncio
import json
import base64
import websockets
from PIL import Image
import io

async def get_ocr(image_path, runpod_url):
    # Load and encode image
    with open(image_path, 'rb') as f:
        img_bytes = f.read()
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    
    # Connect and send
    async with websockets.connect(runpod_url) as websocket:
        # Send image
        await websocket.send(json.dumps({
            "image": f"data:image/png;base64,{base64_str}"
        }))
        
        # Get results
        response = await websocket.recv()
        result = json.loads(response)
        
        if result["status"] == "success":
            print(f"Found {len(result['data']['text_regions'])} text regions")
            for region in result['data']['text_regions']:
                print(f"Text: {region['text']}")
                print(f"Coordinates: {region['coordinates']}")
                print(f"Confidence: {region['confidence']}")
        else:
            print(f"Error: {result['error']}")

# Usage
runpod_url = "wss://YOUR_POD_ID-8765.proxy.runpod.net/"
asyncio.run(get_ocr("image.png", runpod_url))
```

### 3. Response Format

Success response:
```json
{
    "status": "success",
    "data": {
        "text_regions": [
            {
                "text": "Hello World",
                "confidence": 0.98,
                "coordinates": [[10, 20], [100, 20], [100, 40], [10, 40]]
            }
        ],
        "image_dimensions": {
            "width": 1920,
            "height": 1080
        },
        "processing_time": 1.23
    }
}
```

Error response:
```json
{
    "status": "error",
    "error": "Error message here"
}
```

### 4. Simple JavaScript Example

```javascript
const ws = new WebSocket('wss://YOUR_POD_ID-8765.proxy.runpod.net/');

ws.onopen = () => {
    // Convert image to base64
    const base64Image = "data:image/png;base64,YOUR_BASE64_STRING";
    
    // Send to OCR
    ws.send(JSON.stringify({
        image: base64Image
    }));
};

ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    if (result.status === 'success') {
        console.log('OCR Results:', result.data.text_regions);
    }
};
```

## Deployment (For Administrators)

### RunPod Template Settings
- **Container Image**: Use PyTorch 2.1.0 with CUDA 11.8
- **Container Disk**: 20 GB
- **Volume Disk**: 0 GB
- **HTTP Port**: 8765
- **GPU**: Any CUDA 11.8 compatible

### Setup Commands
```bash
cd /workspace
git clone https://github.com/gudenvill/paddle1.git
cd paddle1
chmod +x runpod_setup.sh
./runpod_setup.sh
```

The server will start automatically and show:
```
GPU environment detected: True
```

## Features

- ✅ GPU-accelerated OCR (1-2 seconds per image)
- ✅ Accepts base64 encoded images
- ✅ Returns text with exact pixel coordinates
- ✅ WebSocket for real-time processing
- ✅ Supports English text
- ✅ High accuracy with PaddleOCR

## Notes

- First request may take longer (30-60s) while models download
- Subsequent requests are fast (1-2s with GPU)
- Maximum image size: 10MB (base64 encoded)
- Supports PNG, JPG, JPEG formats

## Getting Your Pod ID

1. Go to RunPod dashboard
2. Find your running pod
3. The pod ID is shown (e.g., `mfn9rzbtwrg5c8`)
4. Your WebSocket URL is: `wss://[POD_ID]-8765.proxy.runpod.net/`