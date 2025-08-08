from paddleocr import PaddleOCR
import numpy as np
from typing import List
import sys
import os

# Import our custom types
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import ocr_types.types as data_types

def recognize_text(ocr_client: PaddleOCR, image: np.ndarray):
    """
    Perform full OCR on image (detection + recognition) using PaddleOCR.
    
    This is the ONLY function in this file (following GOLDEN RULE).
    It finds WHERE text is located AND WHAT the text says.
    
    Args:
        ocr_client: Initialized PaddleOCR client
        image: Input image as numpy array
        
    Returns:
        List of RecognitionResult objects with bounding boxes and text
        
    Raises:
        Exception: If OCR processing fails
    """
    try:
        # Perform OCR - this does both detection and recognition
        raw_results = ocr_client.ocr(image)
        
        print(f"🔍 Debug - Raw OCR results type: {type(raw_results)}")
        
        if not raw_results or len(raw_results) == 0:
            print("⚠️  No OCR results returned")
            return []
            
        # PaddleOCR 2.8.1 returns a list, extract the first result (for single image)
        ocr_results = raw_results[0] if isinstance(raw_results, list) else raw_results
        print(f"🔍 Debug - OCR results type: {type(ocr_results)}")
        print(f"🔍 Debug - OCR results length: {len(ocr_results) if ocr_results else 0}")
        
        # Return the raw results for parse_results to handle
        # PaddleOCR 2.8.1 format: list of [bbox_points, (text, confidence)]
        return ocr_results
        
    except Exception as e:
        error_msg = f"OCR recognition failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)