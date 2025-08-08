#!/usr/bin/env python3
"""
Simple test to verify input image and see OCR raw results.
"""

import cv2
import os
from paddleocr import PaddleOCR

def test_image():
    # Check if input image exists
    input_path = "input/1.png"
    
    if not os.path.exists(input_path):
        print(f"❌ Input image not found: {input_path}")
        print("Please add an image to input/1.png")
        return
    
    # Load and check image
    image = cv2.imread(input_path)
    if image is None:
        print(f"❌ Could not load image: {input_path}")
        return
    
    print(f"✅ Image loaded successfully")
    print(f"   📏 Dimensions: {image.shape}")
    print(f"   📄 File size: {os.path.getsize(input_path)} bytes")
    
    # Test OCR directly
    print("\n🔍 Testing PaddleOCR directly...")
    try:
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )
        
        result = ocr.ocr(input_path)  # Pass path directly
        print(f"✅ OCR completed")
        print(f"📊 Raw result: {result}")
        
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image() 