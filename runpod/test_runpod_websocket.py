#!/usr/bin/env python3
"""
Test RunPod WebSocket OCR Server
Connects to RunPod endpoint and sends base64 image for OCR
"""

import asyncio
import json
import base64
import websockets
from PIL import Image
import io
import sys

async def test_runpod_ocr():
    # RunPod WebSocket URL (change http to ws)
    runpod_url = "wss://a8janwh1fpq1ne-8765.proxy.runpod.net/"
    
    # Load test image
    image_path = "input/2.png"
    
    print("🚀 RunPod WebSocket OCR Test")
    print(f"📡 Server: {runpod_url}")
    print(f"📸 Image: {image_path}")
    
    try:
        # Load and encode image
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            print(f"✅ Image loaded: {img.size[0]}x{img.size[1]} pixels")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            base64_str = base64.b64encode(img_bytes).decode('utf-8')
            print(f"✅ Encoded to base64 ({len(base64_str)} chars)")
        
        # Connect to WebSocket
        print(f"\n🔗 Connecting to RunPod WebSocket...")
        async with websockets.connect(runpod_url) as websocket:
            print("✅ Connected!")
            
            # Send image
            request = {
                "image": f"data:image/png;base64,{base64_str}"
            }
            
            print("📤 Sending image...")
            await websocket.send(json.dumps(request))
            
            # Receive response
            print("⏳ Waiting for OCR results...")
            response = await websocket.recv()
            result = json.loads(response)
            
            # Parse results
            if result.get("metadata", {}).get("success"):
                metadata = result["metadata"]
                print(f"\n✅ OCR SUCCESS!")
                print(f"📊 Processing time: {metadata['processing_time']:.2f}s")
                print(f"🔤 Text regions found: {metadata['total_text_regions']}")
                print(f"🖼️ Image dimensions: {metadata['image_dimensions']}")
                
                # Show first 5 text findings
                if result.get("data", {}).get("text_findings"):
                    print(f"\n📝 Sample text findings (first 5):")
                    for i, finding in enumerate(result["data"]["text_findings"][:5], 1):
                        text = finding["text"]
                        conf = finding["confidence"]
                        coords = finding["coordinates"]
                        tl = coords["top_left"]
                        br = coords["bottom_right"]
                        print(f"   {i}. '{text}' (conf: {conf:.1%}) at [{tl[0]},{tl[1]} -> {br[0]},{br[1]}]")
            else:
                error = result.get("metadata", {}).get("error", {})
                print(f"\n❌ OCR FAILED!")
                print(f"Error: {error.get('message', 'Unknown error')}")
                if error.get("details"):
                    print(f"Details: {error['details']}")
                    
    except asyncio.TimeoutError:
        print("❌ Connection timeout - server may still be initializing")
        print("   Try again in a minute after models are loaded")
    except FileNotFoundError:
        print(f"❌ Image file not found: {image_path}")
    except Exception as e:
        if "websocket" in str(type(e)).lower():
            print(f"❌ WebSocket error: {e}")
            print("   The server may not be ready yet")
        else:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    asyncio.run(test_runpod_ocr())
    print("="*60)
