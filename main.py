#!/usr/bin/env python3
"""
Main entry point for PaddleOCR project.
Batch processing multiple images with client reuse.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

# Import our modules with fixed path
from utils.ocr_client import get_ocr_client
import ocr_types.types as data_types

def process_image_with_client(image_path: str, ocr_client, config: data_types.OCRConfig) -> dict:
    """
    Process image using an existing OCR client (no model reloading).
    """
    try:
        from pipeline.load_image import load_image
        from pipeline.recognize_text import recognize_text
        from pipeline.parse_results import parse_results
        from pipeline.format_json import format_json
        from visualization.create_visualization import create_visualization
        from error.handle_errors import handle_ocr_error
        
        start_time = time.time()
        
        # Step 1: Load image from file path
        image = load_image(image_path)
        image_dimensions = (image.shape[1], image.shape[0])
        
        # Step 2: Use EXISTING OCR client (no reload!)
        recognition_results = recognize_text(ocr_client, image)
        
        # Step 3: Parse results
        findings = parse_results(recognition_results)
        
        # Step 4: Create visualization if enabled
        visualization_result = None
        if config and config.enable_visualization:
            visualization_result = create_visualization(
                image=image,
                findings=findings,
                viz_config=config.viz_config,
                image_path=image_path
            )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Step 5: Format final JSON
        json_result = format_json(
            findings=findings,
            processing_time=processing_time,
            image_dimensions=image_dimensions,
            visualization=visualization_result
        )
        
        return json_result
        
    except Exception as e:
        from error.handle_errors import handle_ocr_error
        return handle_ocr_error(e, image_path)

def process_multiple_images(image_paths: List[str], output_dir: str = "output") -> Dict:
    """
    Process multiple images with optimized client reuse.
    
    Args:
        image_paths: List of image file paths to process
        output_dir: Directory to save results
        
    Returns:
        Dict with overall results and individual image results
    """
    
    print(f"🚀 Starting PaddleOCR Batch Processing - {len(image_paths)} images")
    print("=" * 70)
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Configure OCR
    viz_config = data_types.VisualizationConfig(
        show_bboxes=True,
        show_text=True,
        show_confidence=True,
        bbox_color=(0, 255, 0),
        text_color=(255, 0, 0),
        bbox_thickness=2,
        font_scale=0.8,
        save_annotated_image=True,
        output_path=None  # Will be set per image
    )
    
    ocr_config = data_types.OCRConfig(
        language=data_types.OCRLanguage.ENGLISH,
        enable_visualization=True,
        viz_config=viz_config
    )
    
    # Results storage
    batch_results = {
        "batch_info": {
            "total_images": len(image_paths),
            "processed_images": 0,
            "failed_images": 0,
            "total_processing_time": 0,
            "model_loading_time": 0,
            "average_per_image": 0
        },
        "individual_results": []
    }
    
    try:
        # Step 1: Create OCR client ONCE for all images
        print("📥 Creating OCR client (one-time setup)...")
        client_start = time.time()
        ocr_client = get_ocr_client(ocr_config)
        model_loading_time = time.time() - client_start
        batch_results["batch_info"]["model_loading_time"] = model_loading_time
        
        print(f"✅ OCR client ready in {model_loading_time:.2f}s")
        print("=" * 70)
        
        # Step 2: Process each image with the same client
        batch_start = time.time()
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"🔄 Processing image {i}/{len(image_paths)}: {os.path.basename(image_path)}")
            
            # Check if file exists
            if not os.path.exists(image_path):
                print(f"   ❌ File not found: {image_path}")
                batch_results["batch_info"]["failed_images"] += 1
                batch_results["individual_results"].append({
                    "image_path": image_path,
                    "success": False,
                    "error": "File not found",
                    "processing_time": 0
                })
                continue
            
            # Set output paths for this image
            base_name = Path(image_path).stem
            output_image_path = f"{output_dir}/{base_name}_result.png"
            output_json_path = f"{output_dir}/{base_name}_result.json"
            
            # Update visualization config for this image
            ocr_config.viz_config.output_path = output_image_path
            
            # Process the image
            image_start = time.time()
            try:
                result = process_image_with_client(image_path, ocr_client, ocr_config)
                image_processing_time = time.time() - image_start
                
                # Save JSON result
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                # Track success
                if result["metadata"]["success"]:
                    findings_count = result["metadata"]["total_text_regions"]
                    print(f"   ✅ Success: {findings_count} text regions found in {image_processing_time:.2f}s")
                    batch_results["batch_info"]["processed_images"] += 1
                    
                    batch_results["individual_results"].append({
                        "image_path": image_path,
                        "success": True,
                        "text_regions_found": findings_count,
                        "processing_time": image_processing_time,
                        "output_json": output_json_path,
                        "output_image": output_image_path if result["metadata"].get("has_visualization") else None
                    })
                else:
                    print(f"   ❌ Processing failed: {result['metadata']['error']['message']}")
                    batch_results["batch_info"]["failed_images"] += 1
                    batch_results["individual_results"].append({
                        "image_path": image_path,
                        "success": False,
                        "error": result["metadata"]["error"]["message"],
                        "processing_time": image_processing_time
                    })
                    
            except Exception as e:
                image_processing_time = time.time() - image_start
                print(f"   ❌ Error processing {image_path}: {str(e)}")
                batch_results["batch_info"]["failed_images"] += 1
                batch_results["individual_results"].append({
                    "image_path": image_path,
                    "success": False,
                    "error": str(e),
                    "processing_time": image_processing_time
                })
        
        # Calculate final statistics
        total_batch_time = time.time() - batch_start
        batch_results["batch_info"]["total_processing_time"] = total_batch_time
        
        if batch_results["batch_info"]["processed_images"] > 0:
            batch_results["batch_info"]["average_per_image"] = total_batch_time / len(image_paths)
        
        # Print summary
        print("=" * 70)
        print("📊 BATCH PROCESSING SUMMARY:")
        print(f"   • Total images:           {batch_results['batch_info']['total_images']}")
        print(f"   • Successfully processed: {batch_results['batch_info']['processed_images']}")
        print(f"   • Failed:                 {batch_results['batch_info']['failed_images']}")
        print(f"   • Model loading time:     {model_loading_time:.2f}s (one-time cost)")
        print(f"   • Total processing time:  {total_batch_time:.2f}s")
        print(f"   • Average per image:      {batch_results['batch_info']['average_per_image']:.2f}s")
        
        if len(image_paths) > 1:
            efficiency = model_loading_time / total_batch_time
            print(f"   • Efficiency gain:        {efficiency:.1%} saved by reusing client")
        
        # Save batch summary
        batch_summary_path = f"{output_dir}/batch_summary.json"
        with open(batch_summary_path, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False)
        
        print(f"   • Batch summary saved:    {batch_summary_path}")
        print("=" * 70)
        
        return batch_results
        
    except Exception as e:
        print(f"❌ Batch processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return batch_results

def main():
    """
    Main function with multiple image processing options.
    """
    
    # Option 1: Define multiple image paths directly
    image_paths = [
        "input/1.png",
        "input/2.png",
        "input/3.png",
        "input/4.png",
        "input/5.png",
        "input/6.png",
        "input/7.png",
        "input/8.png",
        "input/9.png",
        "input/10.png",
        "input/11.png",
        "input/12.png",
        "input/13.png",
        "input/14.png",
        "input/15.png",
        "input/16.png",
        "input/17.png",
        "input/18.png",
        "input/19.png",
        "input/20.png",
        "input/21.png",
        "input/22.png",
        "input/23.png",
        "input/24.png",
        "input/25.png",
        "input/26.png",
        "input/27.png",
        "input/28.png",
        "input/29.png",
        "input/30.png",
        "input/31.png",
        "input/32.png",
        "input/33.png",
        "input/34.png",
        "input/35.png",
        "input/36.png",
        "input/37.png",
        "input/38.png",
        "input/39.png",
        "input/40.png",
        "input/41.png",
        "input/42.png",
        "input/43.png",
        "input/44.png",
        "input/45.png",
        "input/46.png",
        "input/47.png",
        "input/48.png",
        "input/49.png",
        "input/50.png",
        "input/51.png",
        "input/52.png",
        "input/53.png",
    ]
    
    # Option 2: Process all images in input directory
    input_dir = "input"
    if os.path.exists(input_dir):
        # Get all image files from input directory
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.pdf'}
        auto_paths = []
        for file in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file)
            if os.path.isfile(file_path) and Path(file).suffix.lower() in image_extensions:
                auto_paths.append(file_path)
        
        if auto_paths:
            print(f"🔍 Found {len(auto_paths)} images in {input_dir}/ directory:")
            for path in auto_paths:
                print(f"   • {os.path.basename(path)}")
            print()
            
            # Use auto-discovered paths if no manual paths specified
            if len(image_paths) == 1 and not os.path.exists(image_paths[0]):
                image_paths = auto_paths
    
    # Create input directory if it doesn't exist
    Path("input").mkdir(exist_ok=True)
    
    if not image_paths or not any(os.path.exists(path) for path in image_paths):
        print("❌ No valid image files found!")
        print("💡 Please add image files to the 'input/' directory or update the image_paths list in main()")
        print("   Supported formats: PNG, JPG, JPEG, BMP, TIFF, PDF")
        return
    
    # Filter to existing files only
    existing_paths = [path for path in image_paths if os.path.exists(path)]
    
    if len(existing_paths) != len(image_paths):
        missing = [path for path in image_paths if not os.path.exists(path)]
        print(f"⚠️  Warning: {len(missing)} files not found: {missing}")
    
    if existing_paths:
        print(f"📋 Processing {len(existing_paths)} images with client reuse optimization")
        results = process_multiple_images(existing_paths)
        
        if results["batch_info"]["processed_images"] > 0:
            print("🎉 Batch processing completed successfully!")
        else:
            print("😞 No images were processed successfully")

if __name__ == "__main__":
    print("🔤 PaddleOCR Project - Batch Processing with Client Reuse")
    print("Following GOLDEN RULE Architecture - One Function Per File")
    print()
    main()