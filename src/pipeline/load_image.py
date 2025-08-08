import cv2
import numpy as np
import os
from typing import Union
import sys

# Import our custom types for error handling
# Fixed import path

def load_image(image_path: str) -> np.ndarray:
    """
    Load an image from file path and return it as numpy array for OCR processing.
    
    This is the ONLY function in this file (following GOLDEN RULE).
    It loads an image file and converts it to the format expected by PaddleOCR.
    
    Args:
        image_path: Path to the image file (supports common formats: jpg, png, bmp, etc.)
        
    Returns:
        np.ndarray: Image as numpy array in BGR color format (OpenCV format)
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If file exists but cannot be loaded as image
        
    Example:
        image = load_image("/path/to/document.jpg")
        print(f"Image shape: {image.shape}")  # (height, width, channels)
        print(f"Image dtype: {image.dtype}")  # uint8
    """
    
    # Validate file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Validate it's actually a file (not a directory)
    if not os.path.isfile(image_path):
        raise ValueError(f"Path is not a file: {image_path}")
    
    # Load image using OpenCV
    # cv2.imread returns None if file cannot be loaded as image
    image = cv2.imread(image_path)
    
    # Check if image was loaded successfully
    if image is None:
        raise ValueError(f"Could not load image from: {image_path}. "
                        f"Ensure it's a valid image file (jpg, png, bmp, etc.)")
    
    # PaddleOCR expects images in BGR format (which cv2.imread provides by default)
    # No conversion needed - return as-is
    return image