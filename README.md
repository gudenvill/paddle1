# PaddleOCR WebSocket Server

A high-performance OCR WebSocket server that processes base64-encoded images and returns text detection results with exact pixel coordinates. Built with PaddleOCR and optimized for GPU acceleration.

## Features

- 🚀 **WebSocket API** - Real-time OCR processing via WebSocket connection
- 📸 **Base64 Input** - Accepts base64-encoded images (with or without data URL prefix)
- 📍 **Exact Coordinates** - Returns precise pixel coordinates for each text region
- 🎯 **High Accuracy** - Uses PaddleOCR v5 detection + v4 English recognition models
- ⚡ **GPU Support** - Automatically detects and uses GPU when available
- 🔄 **Persistent Connection** - Reuses OCR models across requests for efficiency

## Quick Start

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the WebSocket server
python websocket_server.py
```

Server will start on `ws://localhost:8765`

### Running with Docker

```bash
# Build the Docker image
docker build -t paddle-ocr-server .

# Run with GPU support
docker run --gpus all -p 8765:8765 paddle-ocr-server

# Run without GPU
docker run -p 8765:8765 paddle-ocr-server
```

## API Documentation

### WebSocket Endpoint

Connect to: `ws://localhost:8765` (or your server address)

### Request Format

Send a JSON message with the following structure:

```json
{
  "image": "<base64_encoded_image_string>"
}
```

The `image` field can be:
- Raw base64 string: `"iVBORw0KGgoAAAANSUhEUgAAAAUA..."`
- Data URL format: `"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA..."`
- Supports PNG, JPG, JPEG, BMP formats

### Response Format

The server returns a JSON response with the following structure:

```json
{
  "findings": [
    {
      "text": "Hello World",
      "confidence": 0.9876,
      "coordinates": {
        "top_left": [100, 50],
        "top_right": [200, 50],
        "bottom_right": [200, 75],
        "bottom_left": [100, 75]
      }
    }
  ],
  "metadata": {
    "success": true,
    "total_text_regions": 15,
    "processing_time": 1.234,
    "image_dimensions": {
      "width": 1920,
      "height": 1080
    },
    "has_visualization": false
  }
}
```

#### Response Fields

**findings** (array): List of detected text regions
- `text` (string): The recognized text content
- `confidence` (float): Recognition confidence score (0.0 to 1.0)
- `coordinates` (object): Exact pixel coordinates of the text bounding box
  - `top_left` [x, y]: Top-left corner coordinates
  - `top_right` [x, y]: Top-right corner coordinates  
  - `bottom_right` [x, y]: Bottom-right corner coordinates
  - `bottom_left` [x, y]: Bottom-left corner coordinates

**metadata** (object): Processing metadata
- `success` (boolean): Whether OCR processing succeeded
- `total_text_regions` (integer): Number of text regions detected
- `processing_time` (float): Time taken to process in seconds
- `image_dimensions` (object): Original image dimensions
  - `width` (integer): Image width in pixels
  - `height` (integer): Image height in pixels
- `has_visualization` (boolean): Always false for WebSocket (no visualization)

### Error Response

If an error occurs, the response will have `success: false`:

```json
{
  "metadata": {
    "success": false,
    "error": {
      "message": "Failed to decode base64 image",
      "details": "Invalid base64 string",
      "timestamp": "2025-08-07T10:30:45.123Z"
    }
  }
}
```

## Client Examples

### Python Client Example

```python
import asyncio
import websockets
import json
import base64

async def ocr_image(image_path):
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Connect to WebSocket server
    async with websockets.connect('ws://localhost:8765') as websocket:
        # Send image for OCR
        request = {"image": image_base64}
        await websocket.send(json.dumps(request))
        
        # Receive result
        response = await websocket.recv()
        result = json.loads(response)
        
        # Process result
        if result['metadata']['success']:
            for finding in result['findings']:
                print(f"Text: {finding['text']}")
                print(f"Confidence: {finding['confidence']:.2%}")
                coords = finding['coordinates']
                print(f"Location: ({coords['top_left'][0]}, {coords['top_left'][1]})")
        
        return result

# Run the client
asyncio.run(ocr_image('test.png'))
```

### JavaScript Client Example

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = function() {
    // Convert image to base64
    const canvas = document.getElementById('myCanvas');
    const base64Image = canvas.toDataURL('image/png').split(',')[1];
    
    // Send for OCR
    ws.send(JSON.stringify({
        image: base64Image
    }));
};

ws.onmessage = function(event) {
    const result = JSON.parse(event.data);
    
    if (result.metadata.success) {
        result.findings.forEach(finding => {
            console.log(`Found text: "${finding.text}" at`, finding.coordinates);
            // Draw bounding box on canvas using coordinates
            drawBoundingBox(finding.coordinates);
        });
    }
};
```

### cURL Example (via websocat)

```bash
# Install websocat first
# Then encode image and send
base64 image.png | jq -Rs '{image: .}' | websocat ws://localhost:8765
```

## Coordinate System

The coordinate system uses standard image coordinates:
- Origin (0,0) is at the **top-left** corner
- X increases to the **right**
- Y increases **downward**
- All coordinates are in **pixels**

Example coordinate interpretation:
```
top_left: [100, 50]     top_right: [200, 50]
    +------------------+
    |                  |
    |   "Hello World"  |
    |                  |
    +------------------+
bottom_left: [100, 75]  bottom_right: [200, 75]
```

## Performance Considerations

1. **Model Loading**: The OCR models are loaded once at server startup (~7-8 seconds)
2. **Processing Time**: Typical processing time is 10-15 seconds per image on CPU, 1-3 seconds on GPU
3. **Image Size**: Larger images take longer. Consider resizing if coordinates aren't critical
4. **Connection Reuse**: Keep WebSocket connection open for multiple requests to avoid handshake overhead

## Environment Variables

- `CUDA_VISIBLE_DEVICES`: Set to GPU ID to use specific GPU (e.g., "0" for first GPU)
- `PYTHONUNBUFFERED`: Set to "1" for immediate log output

## Architecture

The server follows the GOLDEN RULE architecture - one function per file for maximum modularity:

```
src/
├── pipeline/           # OCR processing pipeline
│   ├── recognize_text.py
│   ├── parse_results.py
│   └── format_json.py
├── utils/             # Utilities
│   └── ocr_client.py  # PaddleOCR client initialization
├── ocr_types/         # Type definitions
│   └── types.py       # Data structures
└── error/             # Error handling
    └── handle_errors.py
```

## Troubleshooting

### Issue: Server won't start
- Check if port 8765 is already in use
- Ensure all dependencies are installed
- Check Python version (requires 3.8+)

### Issue: GPU not detected
- Verify CUDA installation
- Check `nvidia-smi` output
- Ensure paddlepaddle-gpu is installed (not regular paddlepaddle)

### Issue: Poor OCR accuracy
- Ensure image quality is good (min 300 DPI recommended)
- Check if text is clear and not rotated
- Verify you're using English models for English text

### Issue: Slow processing
- Consider using GPU for acceleration
- Reduce image size if exact coordinates aren't needed
- Keep WebSocket connection open for multiple requests

## License

This project uses PaddleOCR which is licensed under Apache 2.0.