import os
from typing import List, Optional
import sys

# Import our custom types and functions
# Fixed import path
import ocr_types.types as data_types
from ocr_types.types import TextFinding, VisualizationConfig, VisualizationResult
from visualization.draw_results import draw_results
import numpy as np

def create_visualization(
    image: np.ndarray,
    findings: List[TextFinding],
    viz_config: VisualizationConfig,
    image_path: str
) -> VisualizationResult:
    """
    Create complete visualization of OCR results.
    
    This is the ONLY function in this file (following GOLDEN RULE).
    It orchestrates the visualization process: draw results + save image.
    
    Args:
        image: Original image as numpy array
        findings: List of TextFinding objects to visualize
        viz_config: Configuration for visualization appearance
        image_path: Original image path (used for generating output filename)
        
    Returns:
        VisualizationResult: Contains annotated image and save path info
        
    Example:
        viz_config = VisualizationConfig(save_annotated_image=True)
        viz_result = create_visualization(image, findings, viz_config, "doc.jpg")
        print(f"Visualization saved to: {viz_result.output_path}")
    """
    
    # Step 1: Draw OCR results on the image
    annotated_image = draw_results(image, findings, viz_config)
    
    # Step 2: Handle saving if enabled
    output_path = None
    if viz_config.save_annotated_image:
        # Generate output filename
        if viz_config.output_path:
            output_path = viz_config.output_path
        else:
            # Create default output path based on input filename
            input_dir = os.path.dirname(image_path)
            input_name = os.path.splitext(os.path.basename(image_path))[0]
            output_filename = f"{input_name}_ocr_annotated.jpg"
            output_path = os.path.join(input_dir, output_filename)
        
        # Save the annotated image
        import cv2
        cv2.imwrite(output_path, annotated_image)
    
    # Step 3: Create and return VisualizationResult
    visualization_result = VisualizationResult(
        annotated_image=annotated_image,
        output_path=output_path
    )
    
    return visualization_result