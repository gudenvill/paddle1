#!/usr/bin/env python3
"""
Debug base64 encoding/decoding to ensure image data is preserved
"""

import base64
import io
from PIL import Image
import numpy as np

def test_base64_conversion(image_path: str):
    print(f"Testing base64 conversion for: {image_path}")
    
    # Original image
    with Image.open(image_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        print(f"Original: {img.size[0]}x{img.size[1]} pixels, mode: {img.mode}")
        original_array = np.array(img)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        print(f"Base64 length: {len(base64_str)} chars")
        
        # Decode back
        decoded_bytes = base64.b64decode(base64_str)
        decoded_img = Image.open(io.BytesIO(decoded_bytes))
        if decoded_img.mode != 'RGB':
            decoded_img = decoded_img.convert('RGB')
        decoded_array = np.array(decoded_img)
        
        print(f"Decoded: {decoded_img.size[0]}x{decoded_img.size[1]} pixels, mode: {decoded_img.mode}")
        
        # Compare
        if np.array_equal(original_array, decoded_array):
            print("✅ Perfect match! Base64 conversion preserves image data")
        else:
            diff = np.sum(original_array != decoded_array)
            total = original_array.size
            print(f"⚠️ Mismatch: {diff}/{total} pixels differ ({100*diff/total:.2f}%)")
        
        # Save decoded for visual inspection
        decoded_img.save("debug_decoded.png")
        print("Saved decoded image to debug_decoded.png")
        
        # Test OCR on local image
        print("\nTesting OCR locally on the same image...")
        from paddleocr import PaddleOCR
        import paddle
        
        use_gpu = paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
        print(f"GPU available locally: {use_gpu}")
        
        ocr = PaddleOCR(
            lang="en",
            use_gpu=use_gpu,
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="en_PP-OCRv4_mobile_rec",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )
        
        result = ocr.ocr(decoded_array, cls=False)
        if result and result[0]:
            print(f"✅ OCR found {len(result[0])} text regions locally")
            for i, item in enumerate(result[0][:3]):
                text = item[1][0] if isinstance(item[1], tuple) else item[1]
                print(f"  Sample {i+1}: '{text}'")
        else:
            print("❌ No text detected locally either")

if __name__ == "__main__":
    import sys
    image_path = sys.argv[1] if len(sys.argv) > 1 else "input/1.png"
    test_base64_conversion(image_path)