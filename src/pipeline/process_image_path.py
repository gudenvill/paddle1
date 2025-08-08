import time
from typing import Optional, Tuple
import sys
import os

# Add parent directories to path for imports
# Fixed import path

# Import all our atomic functions
from pipeline.load_image import load_image
from pipeline.recognize_text import recognize_text
from pipeline.parse_results import parse_results
from pipeline.format_json import format_json
from utils.ocr_client import get_ocr_client
from visualization.create_visualization import create_visualization
import ocr_types.types as data_types
from ocr_types.types import OCRConfig, VisualizationResult
from error.handle_errors import handle_ocr_error

def process_image_path(
    image_path: str, 
    config: Optional[OCRConfig] = None
) -> dict:
    """
    Complete OCR pipeline: process image path and return JSON results with optional visualization.
    
    This is the ONLY function in this file (following GOLDEN RULE).
    It orchestrates all atomic functions to create the complete OCR workflow.
    
    Args:
        image_path: Path to image file for OCR processing
        config: Optional OCR configuration, uses defaults if None
        
    Returns:
        dict: Complete JSON structure with OCR results and metadata
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be processed
        RuntimeError: If OCR processing fails
        
    Example:
        # Basic usage
        result = process_image_path("document.jpg")
        print(f"Found {len(result['findings'])} text regions")
        
        # With custom config and visualization
        config = OCRConfig(enable_visualization=True, use_gpu=True)
        result = process_image_path("document.jpg", config)
        print(f"Visualization saved to: {result['metadata']['visualization_path']}")
    """
    
    try:
        # Record start time for performance metrics
        start_time = time.time()
        
        # Step 1: Load image from file path
        image = load_image(image_path)
        
        # Get image dimensions for metadata
        image_dimensions = (image.shape[1], image.shape[0])  # (width, height)
        
        # Step 2: Initialize OCR client with configuration
        ocr_client = get_ocr_client(config)
        
        # Step 3: Recognize text (includes detection + recognition)
        recognition_results = recognize_text(ocr_client, image)
        
        # Step 4: Parse raw results into clean TextFinding objects
        findings = parse_results(recognition_results)
        
        # Step 5: Create visualization if enabled
        visualization_result = None
        if config and config.enable_visualization:
            visualization_result = create_visualization(
                image=image,
                findings=findings,
                viz_config=config.viz_config,
                image_path=image_path
            )
        
        # Calculate total processing time
        processing_time = time.time() - start_time
        
        # Step 6: Format everything into final JSON structure
        json_result = format_json(
            findings=findings,
            processing_time=processing_time,
            image_dimensions=image_dimensions,
            visualization=visualization_result
        )
        
        return json_result
        
    except Exception as e:
        # Handle any errors that occur during processing
        return handle_ocr_error(e, image_path)