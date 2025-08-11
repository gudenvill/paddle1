from typing import List
import sys
import os

# Import our custom types
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import ocr_types.types as data_types

def extract_individual_words(word_box_data, overall_bbox_points):
    """
    Extract individual words with precise coordinates from PaddleOCR word_box_data.
    
    word_box_data format: [total_width, [word_list], [position_list], [lang_list]]
    where:
    - word_list: [['F', 'i', 'l', 'e'], ['E', 'd', 'i', 't'], ...]  # Characters per word
    - position_list: [[2, 4, 6, 8], [19, 22, 25, 27], ...]  # Character positions per word
    
    Returns:
        List of WordFinding objects with precise coordinates for each word
    """
    try:
        if not word_box_data or len(word_box_data) < 3:
            return None
            
        total_width, word_char_list, word_pos_list, lang_list = word_box_data
        
        if not word_char_list or not word_pos_list:
            return None
            
        # Calculate overall text region dimensions for coordinate mapping
        overall_x1 = min(point[0] for point in overall_bbox_points)
        overall_y1 = min(point[1] for point in overall_bbox_points)
        overall_x2 = max(point[0] for point in overall_bbox_points)
        overall_y2 = max(point[1] for point in overall_bbox_points)
        overall_width = overall_x2 - overall_x1
        overall_height = overall_y2 - overall_y1
        
        individual_words = []
        
        for i, (chars, positions) in enumerate(zip(word_char_list, word_pos_list)):
            if not chars or not positions:
                continue
                
            # Reconstruct word from characters
            word = ''.join(chars)
            
            # Calculate word coordinates based on character positions
            word_start_pos = min(positions)
            word_end_pos = max(positions) 
            
            # Map from relative text positions to absolute coordinates
            # This is approximate - PaddleOCR gives us relative positions within the text
            word_start_x = overall_x1 + (word_start_pos / total_width) * overall_width
            word_end_x = overall_x1 + (word_end_pos / total_width) * overall_width
            
            # Create bounding box for this word (approximate height same as overall)
            # Ensure all coordinates are Python int, not numpy int64
            word_coords = data_types.BoundingBox(
                top_left=(int(float(word_start_x)), int(float(overall_y1))),
                top_right=(int(float(word_end_x)), int(float(overall_y1))),
                bottom_right=(int(float(word_end_x)), int(float(overall_y2))),
                bottom_left=(int(float(word_start_x)), int(float(overall_y2)))
            )
            
            # Extract character positions if needed
            char_positions = []
            for j, (char, pos) in enumerate(zip(chars, positions)):
                char_x = overall_x1 + (pos / total_width) * overall_width
                char_y = (overall_y1 + overall_y2) / 2  # Center vertically
                # Ensure Python int, not numpy int64
                char_positions.append((char, (int(float(char_x)), int(float(char_y)))))
            
            word_finding = data_types.WordFinding(
                word=word,
                confidence=1.0,  # PaddleOCR doesn't give word-level confidence, use overall
                coordinates=word_coords,
                character_positions=char_positions
            )
            
            individual_words.append(word_finding)
            print(f"    📝 Extracted word: '{word}' at ({word_start_x:.0f},{overall_y1})")
            
        return individual_words
        
    except Exception as e:
        print(f"⚠️  Error extracting individual words: {str(e)}")
        return None

def parse_results(recognition_results) -> List[data_types.TextFinding]:
    """
    Parse PaddleOCR results into multi-dimensional TextFinding objects.
    
    This handles PaddleOCR 2.8.1 format with return_word_box=True:
    - Overall text region: [bbox_points, (text, confidence, word_box_data)]
    - Individual words with coordinates
    - Character-level positions
    - Raw word_box_data for maximum flexibility
    
    Args:
        recognition_results: List from PaddleOCR with format [[bbox], (text, conf, word_data)]
        
    Returns:
        List of TextFinding objects with multi-dimensional data
        
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
                # Ensure all coordinates are Python int, not numpy int64
                coords = data_types.BoundingBox(
                    top_left=(int(float(bbox_points[0][0])), int(float(bbox_points[0][1]))),
                    top_right=(int(float(bbox_points[1][0])), int(float(bbox_points[1][1]))),
                    bottom_right=(int(float(bbox_points[2][0])), int(float(bbox_points[2][1]))),
                    bottom_left=(int(float(bbox_points[3][0])), int(float(bbox_points[3][1])))
                )
                
                # Extract individual words if word_box_data is available
                individual_words = None
                if word_box_data is not None:
                    individual_words = extract_individual_words(word_box_data, bbox_points)
                
                finding = data_types.TextFinding(
                    text=text.strip(),  # Clean whitespace
                    confidence=float(confidence),
                    coordinates=coords,
                    individual_words=individual_words,
                    raw_word_box_data=word_box_data  # Store raw data for maximum flexibility
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