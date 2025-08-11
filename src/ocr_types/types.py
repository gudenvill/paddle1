from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum
import numpy as np

@dataclass
class BoundingBox:
    """Represents coordinates of a text region in the image"""
    top_left: Tuple[int, int]      # (x, y) coordinates of top-left corner
    top_right: Tuple[int, int]     # (x, y) coordinates of top-right corner  
    bottom_right: Tuple[int, int]  # (x, y) coordinates of bottom-right corner
    bottom_left: Tuple[int, int]   # (x, y) coordinates of bottom-left corner
    
    def to_dict(self) -> dict:
        """Convert bounding box to dictionary format"""
        return {
            "top_left": self.top_left,
            "top_right": self.top_right, 
            "bottom_right": self.bottom_right,
            "bottom_left": self.bottom_left
        }
    
    def get_corner_points(self) -> List[Tuple[int, int]]:
        """Get all 4 corner points as a list for drawing"""
        return [self.top_left, self.top_right, self.bottom_right, self.bottom_left]

@dataclass
class DetectionResult:
    """Raw detection result from PaddleOCR detection step"""
    bbox: BoundingBox    # Where the text is located
    confidence: float    # How confident the detection is (0.0 to 1.0)

@dataclass  
class RecognitionResult:
    """Raw recognition result from PaddleOCR recognition step"""
    text: str           # The actual text content detected
    confidence: float   # How confident the recognition is (0.0 to 1.0)
    bbox: BoundingBox   # Where this text is located

@dataclass
class WordFinding:
    """Individual word with precise coordinates"""
    word: str           # Individual word
    confidence: float   # Confidence for this word
    coordinates: BoundingBox  # Word-level bounding box
    character_positions: Optional[List[Tuple[str, Tuple[int, int]]]] = None  # [(char, (x,y)), ...]
    
    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "confidence": self.confidence,
            "coordinates": self.coordinates.to_dict(),
            "character_positions": self.character_positions
        }

@dataclass
class TextFinding:
    """Final structured result combining detection and recognition with multi-dimensional data"""
    text: str           # The complete recognized text content
    confidence: float   # Overall confidence score
    coordinates: BoundingBox  # Precise location in image
    
    # Multi-dimensional data
    individual_words: Optional[List[WordFinding]] = None  # Word-by-word breakdown
    raw_word_box_data: Optional[any] = None  # Raw PaddleOCR word_box_data for maximum flexibility
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        result = {
            "text": self.text,
            "confidence": self.confidence,
            "coordinates": self.coordinates.to_dict()
        }
        
        if self.individual_words:
            result["individual_words"] = [word.to_dict() for word in self.individual_words]
            
        if self.raw_word_box_data:
            result["raw_word_box_data"] = self.raw_word_box_data
            
        return result

@dataclass
class VisualizationConfig:
    """Configuration for visual representation of OCR results"""
    show_bboxes: bool = True           # Draw bounding boxes around text
    show_text: bool = True             # Show recognized text on image
    show_confidence: bool = True       # Show confidence scores
    bbox_color: Tuple[int, int, int] = (0, 255, 0)    # Green bounding boxes (BGR)
    text_color: Tuple[int, int, int] = (255, 0, 0)    # Blue text (BGR)
    bbox_thickness: int = 2            # Thickness of bounding box lines
    font_scale: float = 0.1            # Size of text overlay
    save_annotated_image: bool = True  # Whether to save the annotated image
    output_path: Optional[str] = None  # Where to save annotated image

@dataclass
class VisualizationResult:
    """Result of visualization processing"""
    annotated_image: np.ndarray        # Image with OCR results drawn on it
    output_path: Optional[str] = None  # Path where image was saved (if saved)
    
    def save_image(self, path: str) -> str:
        """Save the annotated image to specified path"""
        import cv2
        cv2.imwrite(path, self.annotated_image)
        return path

@dataclass
class OCRResults:
    """Complete OCR processing results with optional visualization"""
    findings: List[TextFinding]  # All text findings in the image
    processing_time: float       # Time taken to process (in seconds)
    image_dimensions: Tuple[int, int]  # (width, height) of processed image
    total_text_regions: int      # Number of text regions found
    visualization: Optional[VisualizationResult] = None  # Visual representation
    
    def to_dict(self) -> dict:
        """Convert entire result to JSON-serializable dictionary"""
        result = {
            "findings": [finding.to_dict() for finding in self.findings],
            "metadata": {
                "processing_time": self.processing_time,
                "image_dimensions": {
                    "width": self.image_dimensions[0],
                    "height": self.image_dimensions[1]
                },
                "total_text_regions": self.total_text_regions,
                "has_visualization": self.visualization is not None
            }
        }
        
        if self.visualization and self.visualization.output_path:
            result["metadata"]["visualization_path"] = self.visualization.output_path
            
        return result

class OCRLanguage(Enum):
    """Supported languages for OCR processing"""
    ENGLISH = "en"
    CHINESE = "ch" 
    JAPANESE = "japan"
    KOREAN = "korean"
    MULTILINGUAL = "multi"

@dataclass
class OCRConfig:
    """MINIMAL Configuration settings for PaddleOCR client - only universally supported options"""
    language: OCRLanguage = OCRLanguage.ENGLISH
    # REMOVED: All potentially unsupported parameters (use_gpu, use_angle_cls, model dirs)
    enable_visualization: bool = True  # Whether to generate visual output
    viz_config: VisualizationConfig = None
    
    def __post_init__(self):
        """Initialize default visualization config if none provided"""
        if self.viz_config is None:
            self.viz_config = VisualizationConfig()