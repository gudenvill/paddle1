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

def detect_text(ocr_client: PaddleOCR, image: np.ndarray) -> List[data_types.DetectionResult]:
    """
    Detect text regions in image using PaddleOCR.
    
    This is the ONLY function in this file (following GOLDEN RULE).
    Since PaddleOCR 3.x does full OCR by default, we extract just the detection info.
    
    Args:
        ocr_client: Initialized PaddleOCR client from get_ocr_client()
        image: Image as numpy array from load_image()
        
    Returns:
        List[DetectionResult]: List of detected text regions with bounding boxes and confidence
    """
    
    # Use the standard OCR method (does detection + recognition)
    raw_results = ocr_client.ocr(image)
    
    # Handle case where no text is detected
    if not raw_results or not raw_results[0]:
        return []
    
    detection_results = []
    
    # Extract only the detection information from full OCR results
    for result in raw_results[0]:
        # PaddleOCR format: [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ('text', confidence)]
        
        bbox_points = result[0]        # The 4 corner points
        text_data = result[1]          # Tuple of (text_content, confidence) 
        confidence = text_data[1]      # Recognition confidence (we use this as detection confidence)
        
        # Convert to our BoundingBox format
        bbox = data_types.BoundingBox(
            top_left=(int(bbox_points[0][0]), int(bbox_points[0][1])),
            top_right=(int(bbox_points[1][0]), int(bbox_points[1][1])),
            bottom_right=(int(bbox_points[2][0]), int(bbox_points[2][1])),
            bottom_left=(int(bbox_points[3][0]), int(bbox_points[3][1]))
        )
        
        # Create DetectionResult object (using recognition confidence as detection confidence)
        detection_result = data_types.DetectionResult(
            bbox=bbox,
            confidence=float(confidence)
        )
        
        detection_results.append(detection_result)
    
    return detection_results