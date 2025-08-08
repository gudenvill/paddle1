import cv2
import numpy as np
from typing import List, Tuple
import sys
import os

# Import our custom types
# Fixed import path
import ocr_types.types as data_types
from ocr_types.types import TextFinding, VisualizationConfig

def draw_results(
    image: np.ndarray, 
    findings: List[TextFinding], 
    viz_config: VisualizationConfig
) -> np.ndarray:
    """
    Draw OCR results (bounding boxes and text) on image.
    
    This is the ONLY function in this file (following GOLDEN RULE).
    It annotates an image with detected text regions and recognized content.
    
    Args:
        image: Original image as numpy array
        findings: List of TextFinding objects with text and coordinates
        viz_config: Configuration for how to draw the annotations
        
    Returns:
        np.ndarray: Annotated image with OCR results drawn on it
        
    Example:
        image = load_image("document.jpg")
        findings = [TextFinding(text="STOP", confidence=0.98, coordinates=bbox)]
        viz_config = VisualizationConfig(show_bboxes=True, show_text=True)
        annotated = draw_results(image, findings, viz_config)
    """
    
    # Create a copy of the image to avoid modifying the original
    annotated_image = image.copy()
    
    # If no findings or visualization disabled, return original
    if not findings:
        return annotated_image
    
    # Draw each text finding
    for i, finding in enumerate(findings):
        
        # Draw bounding box if enabled
        if viz_config.show_bboxes:
            # Get corner points for the bounding box
            points = finding.coordinates.get_corner_points()
            
            # Convert to numpy array for cv2.polylines
            bbox_points = np.array(points, dtype=np.int32)
            
            # Draw bounding box as polygon (handles rotated text)
            cv2.polylines(
                annotated_image, 
                [bbox_points], 
                isClosed=True, 
                color=viz_config.bbox_color,
                thickness=viz_config.bbox_thickness
            )
        
        # Draw text label if enabled
        if viz_config.show_text or viz_config.show_confidence:
            # Position text at top-left corner of bounding box
            text_position = finding.coordinates.top_left
            
            # Build text label
            text_parts = []
            if viz_config.show_text:
                text_parts.append(finding.text)
            if viz_config.show_confidence:
                confidence_str = f"({finding.confidence:.2f})"
                text_parts.append(confidence_str)
            
            text_label = " ".join(text_parts)
            
            # Calculate text size for background rectangle
            (text_width, text_height), baseline = cv2.getTextSize(
                text_label, 
                cv2.FONT_HERSHEY_SIMPLEX, 
                viz_config.font_scale, 
                thickness=1
            )
            
            # Draw background rectangle for text readability
            background_top_left = (
                text_position[0], 
                text_position[1] - text_height - baseline
            )
            background_bottom_right = (
                text_position[0] + text_width,
                text_position[1] + baseline
            )
            
            # Semi-transparent background
            cv2.rectangle(
                annotated_image,
                background_top_left,
                background_bottom_right,
                color=(255, 255, 255),  # White background
                thickness=-1  # Filled rectangle
            )
            
            # Draw the text
            cv2.putText(
                annotated_image,
                text_label,
                text_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                viz_config.font_scale,
                viz_config.text_color,
                thickness=1,
                lineType=cv2.LINE_AA  # Anti-aliased text
            )
    
    return annotated_image