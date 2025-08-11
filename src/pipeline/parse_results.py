from typing import List
import sys
import os

# Import our custom types
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import ocr_types.types as data_types

def parse_results(recognition_results) -> List[data_types.TextFinding]:
    """
    Parse PaddleOCR results into clean TextFinding objects.
    
    This handles PaddleOCR 2.8.1 format: list of [bbox_points, (text, confidence)] tuples
    
    Args:
        recognition_results: List from PaddleOCR with format [[bbox], (text, conf)]
        
    Returns:
        List of TextFinding objects with enhanced metadata
        
    Raises:
        Exception: If parsing fails
    """
    try:
        if not recognition_results:
            print("⚠️  No recognition results to parse")
            return []
            
        print(f"🔍 Debug - Raw OCR results type: {type(recognition_results)}")
        if recognition_results:
            print(f"🔍 Debug - First result sample: {recognition_results[0]}")
            
        findings = []
        
        for i, result in enumerate(recognition_results):
            try:
                # PaddleOCR 2.8.1 format with return_word_box=True: [bbox_points, (text, confidence, word_box_data)]
                if len(result[1]) == 3:
                    # New format with word box data
                    bbox_points, (text, confidence, word_box_data) = result
                else:
                    # Old format without word box data
                    bbox_points, (text, confidence) = result
                    word_box_data = None
                
                # Convert bbox points to BoundingBox object
                # bbox_points is list of 4 corner points: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                coords = data_types.BoundingBox(
                    top_left=(int(bbox_points[0][0]), int(bbox_points[0][1])),
                    top_right=(int(bbox_points[1][0]), int(bbox_points[1][1])),
                    bottom_right=(int(bbox_points[2][0]), int(bbox_points[2][1])),
                    bottom_left=(int(bbox_points[3][0]), int(bbox_points[3][1]))
                )
                
                finding = data_types.TextFinding(
                    text=text.strip(),  # Clean whitespace
                    confidence=float(confidence),
                    coordinates=coords
                )
                
                findings.append(finding)
                print(f"✅ Processed result {i}: '{finding.text}' (confidence: {finding.confidence:.3f})")
                
            except Exception as e:
                print(f"⚠️  Error parsing result {i}: {str(e)}")
                print(f"    Result format: {result}")
                continue
        
        print(f"✅ Total findings parsed: {len(findings)}")
        return findings
        
    except Exception as e:
        error_msg = f"Results parsing failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)