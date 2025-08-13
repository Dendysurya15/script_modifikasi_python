from ultralytics import YOLO
import argparse
import os
from pathlib import Path
import time
import json
import sys
import shutil

def parse_args():
    parser = argparse.ArgumentParser(description='YOLO detection with custom parameters')
    parser.add_argument('--weights', type=str, required=True, help='Path to YOLO weights file')
    parser.add_argument('--folder', type=str, required=True, help='Path to source folder or URL')
    parser.add_argument('--output', type=str, required=True, help='Path to output folder')
    parser.add_argument('--is_annotated', action='store_true', help='Create annotated images for visual verification')
    parser.add_argument('--line-width', type=int, default=2, help='Line width for bounding boxes')
    parser.add_argument('--show-conf', type=bool, default=True, help='Show confidence scores')
    parser.add_argument('--show-labels', type=bool, default=True, help='Show class labels')
    parser.add_argument('--max-det', type=int, default=7000, help='Maximum detections per image')
    parser.add_argument('--imgsz', type=int, default=1280, help='Image size for inference')
    parser.add_argument('--iou', type=float, default=0.2, help='NMS IoU threshold')
    parser.add_argument('--conf', type=float, default=0.2, help='Confidence threshold')
    return parser.parse_args()

def create_output_structure(output_path, create_annotated=False):
    """Create the output folder structure"""
    output_path = Path(output_path)
    images_dir = output_path / "images"
    labels_dir = output_path / "labels"
    
    # Create directories if they don't exist
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    
    annotated_dir = None
    if create_annotated:
        annotated_dir = output_path / "annotated"  # For visual verification
        annotated_dir.mkdir(parents=True, exist_ok=True)
    
    return images_dir, labels_dir, annotated_dir

def save_yolo_labels(results, labels_dir, image_name):
    """Save YOLO format labels to txt file"""
    # Change extension to .txt
    label_file = labels_dir / f"{Path(image_name).stem}.txt"
    
    with open(label_file, 'w') as f:
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get class id, confidence, and normalized coordinates
                    class_id = int(box.cls.cpu().numpy()[0])
                    confidence = float(box.conf.cpu().numpy()[0])
                    
                    # Get normalized coordinates (x_center, y_center, width, height)
                    x_center, y_center, width, height = box.xywhn.cpu().numpy()[0]
                    
                    # Write in YOLO format: class_id x_center y_center width height
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def save_annotated_image(results, annotated_dir, image_name):
    """Save annotated image for visual verification"""
    for result in results:
        if hasattr(result, 'save'):
            # Get the annotated image
            annotated_img = result.plot()
            
            # Save using cv2 or PIL
            import cv2
            annotated_path = annotated_dir / image_name
            cv2.imwrite(str(annotated_path), annotated_img)
            break

def main():
    start_time = time.time()
    args = parse_args()
    
    # Create output directory structure
    images_dir, labels_dir, annotated_dir = create_output_structure(args.output, args.is_annotated)
    
    model = YOLO(args.weights)
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
    image_files = [f for f in Path(args.folder).rglob('*') if f.suffix.lower() in valid_extensions]
    total_files = len(image_files)
    processed = 0
    
    for img_path in image_files:
        processed += 1
        
        # Run YOLO inference (save=False, we'll handle saving manually)
        results = model(
            str(img_path),
            line_width=args.line_width,
            show_conf=args.show_conf,
            show_labels=args.show_labels,
            max_det=args.max_det,
            imgsz=args.imgsz,
            iou=args.iou,
            conf=args.conf,
            save=False
        )
        
        # Copy original image to images folder
        dest_image_path = images_dir / img_path.name
        shutil.copy2(img_path, dest_image_path)
        
        # Save YOLO format labels
        save_yolo_labels(results, labels_dir, img_path.name)
        
        # Save annotated image for verification (only if requested)
        if args.is_annotated and annotated_dir:
            save_annotated_image(results, annotated_dir, img_path.name)
        
        # Calculate average time per file
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / processed
        
        # Create status message based on what was saved
        status = "Saved image and labels"
        if args.is_annotated:
            status += " and annotated version"
        
        # Output progress as JSON
        progress_info = {
            "processed": processed,
            "total": total_files,
            "current_file": str(img_path.name),
            "status": status,
            "avg_time_per_file": avg_time
        }
        print(json.dumps(progress_info), flush=True)
        sys.stdout.flush()

if __name__ == '__main__':
    main()