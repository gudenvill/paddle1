import time
from typing import Dict, Any
import traceback

def handle_ocr_error(error: Exception, image_path: str) -> Dict[str, Any]:
    """
    Handle and format OCR processing errors into consistent JSON response.
    
    This is the ONLY function in this file (following GOLDEN RULE).
    It converts any exception into a standardized error response format.
    
    Args:
        error: The exception that occurred during OCR processing
        image_path: Path to the image that was being processed
        
    Returns:
        Dict[str, Any]: Standardized error response in JSON format
        
    Example:
        try:
            result = process_image_path("bad_file.jpg")
        except Exception as e:
            error_response = handle_ocr_error(e, "bad_file.jpg")
            print(f"Error: {error_response['metadata']['error']}")
    """
    
    # Determine error type and create appropriate message
    if isinstance(error, FileNotFoundError):
        error_type = "FILE_NOT_FOUND"
        error_message = f"Image file not found: {image_path}"
    elif isinstance(error, ValueError):
        error_type = "INVALID_IMAGE"
        error_message = f"Invalid image file: {str(error)}"
    elif isinstance(error, PermissionError):
        error_type = "PERMISSION_DENIED"
        error_message = f"Permission denied accessing file: {image_path}"
    else:
        error_type = "PROCESSING_ERROR"
        error_message = f"OCR processing failed: {str(error)}"
    
    # Create standardized error response
    error_response = {
        "findings": [],  # Empty findings array
        "metadata": {
            "processing_time": 0.0,
            "image_dimensions": {"width": 0, "height": 0},
            "total_text_regions": 0,
            "timestamp": time.time(),
            "success": False,
            "error": {
                "type": error_type,
                "message": error_message,
                "image_path": image_path,
                "traceback": traceback.format_exc() if error_type == "PROCESSING_ERROR" else None
            },
            "confidence_stats": {
                "average": 0.0,
                "minimum": 0.0,
                "maximum": 0.0
            },
            "text_stats": {
                "total_characters": 0,
                "total_words": 0,
                "longest_text": ""
            }
        }
    }
    
    return error_response