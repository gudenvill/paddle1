from paddleocr import PaddleOCR
from typing import Optional
import sys
import os

# Import our custom types
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import ocr_types.types as data_types

def get_ocr_client(config: Optional[data_types.OCRConfig] = None) -> PaddleOCR:
    # Use default config if none provided
    if config is None:
        config = data_types.OCRConfig()
    
    # For FASTEST performance (mobile models):
    # ocr_client = PaddleOCR(
    #     lang=config.language.value,
    #     text_detection_model_name="PP-OCRv5_mobile_det",
    #     text_recognition_model_name="PP-OCRv5_mobile_rec",
    #     use_doc_orientation_classify=False,
    #     use_doc_unwarping=False,
    #     use_textline_orientation=False
    # )
    
    # For HIGHEST accuracy (keep current):
    # ocr_client = PaddleOCR(
    #     lang=config.language.value,
    #     text_detection_model_name="PP-OCRv5_server_det", 
    #     text_recognition_model_name="PP-OCRv5_server_rec",
    #     use_doc_orientation_classify=False,
    #     use_doc_unwarping=False,
    #     use_textline_orientation=False
    # )
    
    # For ENGLISH-ONLY with GPU support:
    import paddle
    use_gpu = paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
    print(f"GPU environment detected: {use_gpu}")
    
    # Explicitly pass use_gpu parameter
    ocr_client = PaddleOCR(
        lang="en",
        use_gpu=use_gpu,  # Explicitly enable GPU if available
        text_detection_model_name="PP-OCRv5_mobile_det",
        text_recognition_model_name="en_PP-OCRv4_mobile_rec",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        return_word_box=True
    )
    
    return ocr_client
