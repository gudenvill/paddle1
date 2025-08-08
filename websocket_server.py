#!/usr/bin/env python3
"""
WebSocket OCR Server - Processes base64 images and returns OCR results.
Reuses the existing paddle0-based OCR pipeline for maximum reliability.
"""

import asyncio
import json
import base64
import io
import os
import sys
import time
import logging
import traceback
from typing import Dict, Any

import websockets
import numpy as np
from PIL import Image

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

# Import our existing OCR modules
from utils.ocr_client import get_ocr_client
import ocr_types.types as data_types

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketOCRServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.ocr_client = None
        self.ocr_config = None
        
    async def initialize_ocr(self):
        """Initialize OCR client once at startup."""
        logger.info("🚀 Initializing OCR client...")
        start_time = time.time()
        
        # Configure OCR (no visualization for WebSocket)
        self.ocr_config = data_types.OCRConfig(
            language=data_types.OCRLanguage.ENGLISH,
            enable_visualization=False
        )
        
        # Create OCR client
        self.ocr_client = get_ocr_client(self.ocr_config)
        
        init_time = time.time() - start_time
        logger.info(f"✅ OCR client initialized in {init_time:.2f}s")
        
    def base64_to_numpy(self, base64_string: str) -> np.ndarray:
        """Convert base64 string to numpy array (compatible with existing pipeline)."""
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array (same format as our existing pipeline expects)
            numpy_image = np.array(pil_image)
            
            return numpy_image
            
        except Exception as e:
            raise ValueError(f"Failed to decode base64 image: {str(e)}")
    
    async def process_image_websocket(self, base64_image: str) -> Dict[str, Any]:
        """
        Process base64 image using existing OCR pipeline.
        Reuses all the modular functions from src/pipeline/
        """
        try:
            start_time = time.time()
            
            # Convert base64 to numpy array
            image = self.base64_to_numpy(base64_image)
            image_dimensions = (image.shape[1], image.shape[0])  # (width, height)
            
            # Use existing pipeline functions
            from pipeline.recognize_text import recognize_text
            from pipeline.parse_results import parse_results
            from pipeline.format_json import format_json
            
            # Step 1: Use existing OCR client (no reload!)
            recognition_results = recognize_text(self.ocr_client, image)
            
            # Step 2: Parse results (same as file-based version)
            findings = parse_results(recognition_results)
            
            # Step 3: Calculate processing time
            processing_time = time.time() - start_time
            
            # Step 4: Format JSON (no visualization for WebSocket)
            json_result = format_json(
                findings=findings,
                processing_time=processing_time,
                image_dimensions=image_dimensions,
                visualization=None  # No visualization for WebSocket
            )
            
            return json_result
            
        except Exception as e:
            from error.handle_errors import handle_ocr_error
            return handle_ocr_error(e, "websocket_image")
    
    async def handle_client(self, websocket):
        """Handle incoming WebSocket connections."""
        client_addr = websocket.remote_address
        logger.info(f"🔗 New client connected: {client_addr}")
        
        try:
            async for message in websocket:
                try:
                    # Parse incoming message
                    data = json.loads(message)
                    
                    if 'image' not in data:
                        await websocket.send(json.dumps({
                            "success": False,
                            "error": "Missing 'image' field in request"
                        }))
                        continue
                    
                    logger.info(f"📸 Processing image from {client_addr}")
                    
                    # Process the image
                    result = await self.process_image_websocket(data['image'])
                    
                    # Send result back to client
                    await websocket.send(json.dumps(result))
                    
                    # Log success
                    if result.get("metadata", {}).get("success", False):
                        text_count = result.get("metadata", {}).get("total_text_regions", 0)
                        proc_time = result.get("metadata", {}).get("processing_time", 0)
                        logger.info(f"✅ Sent result to {client_addr}: {text_count} text regions in {proc_time:.2f}s")
                    else:
                        error_msg = result.get("metadata", {}).get("error", {}).get("message", "Unknown error")
                        logger.warning(f"❌ Processing failed for {client_addr}: {error_msg}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Invalid JSON from {client_addr}")
                    await websocket.send(json.dumps({
                        "success": False,
                        "error": "Invalid JSON format"
                    }))
                except Exception as e:
                    logger.error(f"❌ Error processing request from {client_addr}: {str(e)}")
                    await websocket.send(json.dumps({
                        "success": False,
                        "error": f"Server error: {str(e)}"
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Client disconnected: {client_addr}")
        except Exception as e:
            logger.error(f"❌ Connection error with {client_addr}: {str(e)}")
    
    async def start_server(self):
        """Start the WebSocket server."""
        # Initialize OCR first
        await self.initialize_ocr()
        
        # Start WebSocket server
        logger.info(f"🌐 Starting WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info("🚀 WebSocket OCR Server is running!")
            logger.info(f"📡 Listening on ws://{self.host}:{self.port}")
            logger.info("💡 Send JSON with 'image' field containing base64-encoded image")
            logger.info("🔄 Press Ctrl+C to stop server")
            
            # Keep server running
            await asyncio.Future()  # run forever

async def main():
    """Main entry point."""
    server = WebSocketOCRServer(host="0.0.0.0", port=8765)
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🔤 WebSocket OCR Server - Base64 Image Processing")
    print("Following GOLDEN RULE Architecture - Reusing Existing Pipeline")
    print()
    
    asyncio.run(main())