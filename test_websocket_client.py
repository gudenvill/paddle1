#!/usr/bin/env python3
"""
WebSocket OCR Test Client - Tests the server with base64 images.
"""

import asyncio
import json
import base64
import websockets
import sys
from pathlib import Path

async def test_ocr_websocket(image_path: str, server_url: str = "ws://localhost:8765"):
    """Test OCR WebSocket with a local image file."""
    
    print(f"🔧 Testing WebSocket OCR server...")
    print(f"📡 Server: {server_url}")
    print(f"📸 Image: {image_path}")
    
    try:
        # Read and encode image
        if not Path(image_path).exists():
            print(f"❌ Image file not found: {image_path}")
            return
        
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"✅ Image encoded to base64 ({len(base64_image)} chars)")
        
        # Connect to WebSocket server
        async with websockets.connect(server_url) as websocket:
            print("🔗 Connected to WebSocket server")
            
            # Send image for OCR
            request = {
                "image": base64_image
            }
            
            print("📤 Sending image for OCR processing...")
            await websocket.send(json.dumps(request))
            
            # Receive result
            print("📥 Waiting for OCR result...")
            response = await websocket.recv()
            result = json.loads(response)
            
            # Display result
            print("\n" + "="*60)
            print("📊 OCR RESULT:")
            print("="*60)
            
            if result.get("metadata", {}).get("success", False):
                metadata = result["metadata"]
                print(f"✅ Success: {metadata['total_text_regions']} text regions found")
                print(f"⏱️ Processing time: {metadata['processing_time']:.2f}s")
                dims = metadata.get('image_dimensions', {})
                print(f"📐 Image dimensions: {dims.get('width', 0)}x{dims.get('height', 0)}")
                
                print(f"\n📝 Text findings:")
                for i, finding in enumerate(result.get("findings", []), 1):
                    text = finding.get("text", "")
                    conf = finding.get("confidence", 0)
                    coords = finding.get("coordinates", {})
                    
                    # Coordinates are in dictionary format with named corners
                    if coords:
                        tl = coords.get("top_left", [0, 0])
                        br = coords.get("bottom_right", [0, 0])
                        bbox_str = f"[({tl[0]},{tl[1]}), ({br[0]},{br[1]})]"
                    else:
                        bbox_str = "[]"
                    print(f"   {i:2d}. '{text}' (conf: {conf:.3f}) at {bbox_str}")
                    
                    if i >= 10:  # Show first 10 results
                        remaining = len(result.get("findings", [])) - 10
                        if remaining > 0:
                            print(f"   ... and {remaining} more text regions")
                        break
                        
            else:
                error = result.get("metadata", {}).get("error", {})
                print(f"❌ OCR failed: {error.get('message', 'Unknown error')}")
                if error.get("details"):
                    print(f"   Details: {error['details']}")
            
            print("="*60)
            
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Connection closed unexpectedly: {e}")
        print("💡 Check server logs for error details")
    except ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server")
        print("💡 Make sure the server is running: python3 websocket_server.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

async def main():
    """Main test function."""
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default test image
        image_path = "input/1.png"
    
    await test_ocr_websocket(image_path)

if __name__ == "__main__":
    print("🧪 WebSocket OCR Test Client")
    print("Usage: python3 test_websocket_client.py [image_path]")
    print()
    
    asyncio.run(main())