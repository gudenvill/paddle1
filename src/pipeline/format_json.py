from typing import List, Tuple, Optional
import time
import sys
import os

# Import our custom types
# Fixed import path
import ocr_types.types as data_types
from ocr_types.types import TextFinding, OCRResults, VisualizationResult

def format_json(
    findings: List[TextFinding], 
    processing_time: float,
    image_dimensions: Tuple[int, int],
    visualization: Optional[VisualizationResult] = None
) -> dict:
    """
    Format TextFinding objects into final JSON output structure.
    
    This is the ONLY function in this file (following GOLDEN RULE).
    It creates the final JSON-serializable dictionary with all OCR results and metadata.
    
    Args:
        findings: List of clean TextFinding objects from parse_results()
        processing_time: Time taken for OCR processing (in seconds)
        image_dimensions: (width, height) of the processed image
        visualization: Optional visualization result if generated
        
    Returns:
        dict: Complete JSON-serializable result structure
        
    Example:
        findings = parse_results(recognitions)
        json_result = format_json(
            findings=findings,
            processing_time=1.23,
            image_dimensions=(1920, 1080)
        )
        print(json.dumps(json_result, indent=2))
    """
    
    # Create OCRResults object to handle the conversion
    ocr_results = OCRResults(
        findings=findings,
        processing_time=processing_time,
        image_dimensions=image_dimensions,
        total_text_regions=len(findings),
        visualization=visualization
    )
    
    # Use the built-in to_dict() method for consistent formatting
    json_output = ocr_results.to_dict()
    
    # Add additional metadata for API completeness
    json_output["metadata"]["timestamp"] = time.time()
    json_output["metadata"]["success"] = True
    json_output["metadata"]["error"] = None
    
    # Add summary statistics
    if findings:
        confidences = [finding.confidence for finding in findings]
        json_output["metadata"]["confidence_stats"] = {
            "average": sum(confidences) / len(confidences),
            "minimum": min(confidences),
            "maximum": max(confidences)
        }
        
        # Calculate total text length
        total_chars = sum(len(finding.text) for finding in findings)
        json_output["metadata"]["text_stats"] = {
            "total_characters": total_chars,
            "total_words": sum(len(finding.text.split()) for finding in findings),
            "longest_text": max(findings, key=lambda f: len(f.text)).text if findings else ""
        }
    else:
        json_output["metadata"]["confidence_stats"] = {
            "average": 0.0,
            "minimum": 0.0,
            "maximum": 0.0
        }
        json_output["metadata"]["text_stats"] = {
            "total_characters": 0,
            "total_words": 0,
            "longest_text": ""
        }
    
    return json_output