#!/usr/bin/env python3
"""
Test WebSocket OCR with proper base64 data URL format.
This tests the full flow as a real client would send it.
"""

import asyncio
import json
import base64
import websockets
import sys
from pathlib import Path
from PIL import Image
import io

async def test_with_data_url(image_path: str, server_url: str = "ws://localhost:8765"):
    """Test OCR WebSocket with data URL format (like from browser)."""
    
    print(f"🧪 Testing WebSocket OCR with data URL format")
    print(f"📡 Server: {server_url}")
    print(f"📸 Image: {image_path}")
    
    try:
        # Read image
        if not Path(image_path).exists():
            print(f"❌ Image file not found: {image_path}")
            return
        
        # Open with PIL to ensure it's valid
        with Image.open(image_path) as img:
            # Convert to RGB if needed (handles RGBA, grayscale, etc)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            # Determine format from file extension
            fmt = 'PNG' if image_path.lower().endswith('.png') else 'JPEG'
            img.save(img_byte_arr, format=fmt)
            img_bytes = img_byte_arr.getvalue()
            
            print(f"✅ Image loaded: {img.size[0]}x{img.size[1]} pixels, {img.mode} mode")
        
        # Create proper data URL with MIME type
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        mime_type = 'image/png' if fmt == 'PNG' else 'image/jpeg'
        data_url = f"data:{mime_type};base64,{base64_str}"
        
        print(f"✅ Created data URL ({len(data_url)} chars total)")
        print(f"   Format: data:{mime_type};base64,<{len(base64_str)} chars>")
        
        # Connect to WebSocket server
        async with websockets.connect(server_url) as websocket:
            print("🔗 Connected to WebSocket server")
            
            # Test 1: Send with data URL prefix
            print("\n📤 Test 1: Sending image WITH data URL prefix...")
            request_with_prefix = {
                "image": data_url
            }
            
            await websocket.send(json.dumps(request_with_prefix))
            response = await websocket.recv()
            result1 = json.loads(response)
            
            if result1.get("metadata", {}).get("success", False):
                print(f"✅ Test 1 SUCCESS: {result1['metadata']['total_text_regions']} regions found")
            else:
                print(f"❌ Test 1 FAILED: {result1.get('metadata', {}).get('error', {}).get('message', 'Unknown')}")
            
            # Test 2: Send without data URL prefix (raw base64)
            print("\n📤 Test 2: Sending image WITHOUT data URL prefix (raw base64)...")
            request_without_prefix = {
                "image": base64_str
            }
            
            await websocket.send(json.dumps(request_without_prefix))
            response = await websocket.recv()
            result2 = json.loads(response)
            
            if result2.get("metadata", {}).get("success", False):
                print(f"✅ Test 2 SUCCESS: {result2['metadata']['total_text_regions']} regions found")
            else:
                print(f"❌ Test 2 FAILED: {result2.get('metadata', {}).get('error', {}).get('message', 'Unknown')}")
            
            # Compare results
            print("\n" + "="*60)
            print("📊 RESULTS COMPARISON:")
            print("="*60)
            
            if result1.get("metadata", {}).get("success") and result2.get("metadata", {}).get("success"):
                regions1 = result1['metadata']['total_text_regions']
                regions2 = result2['metadata']['total_text_regions']
                time1 = result1['metadata']['processing_time']
                time2 = result2['metadata']['processing_time']
                
                print(f"Data URL format:  {regions1} regions in {time1:.2f}s")
                print(f"Raw base64:       {regions2} regions in {time2:.2f}s")
                
                if regions1 == regions2:
                    print("✅ Both formats produced identical results!")
                else:
                    print(f"⚠️  Different results: {abs(regions1-regions2)} region difference")
                
                # Show sample findings
                print("\n📝 Sample text findings (first 5):")
                for i, finding in enumerate(result1.get("findings", [])[:5], 1):
                    text = finding.get("text", "")
                    conf = finding.get("confidence", 0)
                    coords = finding.get("coordinates", {})
                    tl = coords.get("top_left", [0, 0])
                    br = coords.get("bottom_right", [0, 0])
                    print(f"   {i}. '{text}' (conf: {conf:.1%}) at [{tl[0]},{tl[1]} -> {br[0]},{br[1]}]")
                    
            print("="*60)
            
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Connection closed unexpectedly: {e}")
        print("💡 Check server logs for error details")
    except ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server")
        print("💡 Make sure the server is running: python3 websocket_server.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function."""
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default test image
        image_path = "input/1.png"
    
    await test_with_data_url(image_path)

if __name__ == "__main__":
    print("🔬 WebSocket OCR Base64 Format Test")
    print("Tests both data URL and raw base64 formats")
    print("Usage: python3 test_base64_websocket.py [image_path]")
    print()
    
    asyncio.run(main())