import cv2
import os
import argparse
from tqdm import tqdm
import threading
import subprocess

def is_valid_txt_file(file_path):
    """Check if the txt file exists and is readable"""
    try:
        if not os.path.exists(file_path):
            return False
        with open(file_path, 'r') as f:
            content = f.read().strip()
            # Empty files are valid for YOLO (no objects)
            if not content:
                return True
            # Check if each line has the correct format (class_id x_center y_center width height)
            lines = content.split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 5:
                    return False
                # Check if all values are numeric
                try:
                    float(parts[0])  # class_id (can be float but usually int)
                    for i in range(1, 5):
                        val = float(parts[i])
                        if val < 0 or val > 1:  # YOLO coordinates should be normalized (0-1)
                            print(f"Warning: Coordinate {val} out of range [0,1] in {file_path}")
                except ValueError:
                    return False
        return True
    except Exception as e:
        print(f"Error checking file {file_path}: {e}")
        return False

def flip_yolo_coordinates(class_id, x_center, y_center, width, height, flip_type):
    """
    Flip YOLO format coordinates
    flip_type: 'h' for horizontal, 'v' for vertical, 'hv' for both
    """
    if flip_type == 'h':  # Horizontal flip
        x_center_new = 1.0 - x_center
        y_center_new = y_center
    elif flip_type == 'v':  # Vertical flip
        x_center_new = x_center
        y_center_new = 1.0 - y_center
    elif flip_type == 'hv':  # Both horizontal and vertical
        x_center_new = 1.0 - x_center
        y_center_new = 1.0 - y_center
    else:
        raise ValueError("flip_type must be 'h', 'v', or 'hv'")
    
    return class_id, x_center_new, y_center_new, width, height

def process_image_and_label(image_name, input_folder, label_folder, output_folder):
    """Process a single image and its corresponding label file"""
    
    # Construct paths using os.path.join for cross-platform compatibility
    image_path = os.path.join(input_folder, image_name)
    
    # Check if the image file exists
    if not os.path.isfile(image_path):
        print(f"Skipping non-existent image: {image_path}")
        return

    # Get file path components
    file_path, file_extension = os.path.splitext(image_name)
    base_name = os.path.basename(file_path)
    
    # Generate label file name (same base name but .txt extension)
    # Use the original base name, not one that might already have flip suffix
    original_base_name = base_name
    # Remove any existing flip suffixes to get the original name
    for suffix in ['_h_flip', '_v_flip', '_hv_flip']:
        if original_base_name.endswith(suffix):
            original_base_name = original_base_name[:-len(suffix)]
            break
    
    label_file_name = original_base_name + '.txt'
    label_path = os.path.join(label_folder, label_file_name)
    
    # Check if the txt file is valid
    if not is_valid_txt_file(label_path):
        # Only print if it's the original file, not already flipped images
        if not any(suffix in image_name for suffix in ['_h_flip', '_v_flip', '_hv_flip']):
            print(f"Skipping invalid or missing label file: {label_file_name}")
        return

    print(f"Processing image: {image_path}")

    try:
        # Read image
        img = cv2.imread(image_path)
        
        # Check if the image is successfully loaded
        if img is None:
            print(f"Error: Unable to read image file: {image_path}")
            return

        # Read original labels
        labels = []
        with open(label_path, 'r') as f:
            content = f.read().strip()
            if content:  # Only process if file is not empty
                for line in content.split('\n'):
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(float(parts[0]))  # Convert to int for class_id
                        x_center = float(parts[1])
                        y_center = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        labels.append((class_id, x_center, y_center, width, height))

        # Process horizontal flip
        if "_h_flip" not in image_name:
            img_flipped_horizontal = cv2.flip(img, 1)
            
            if img_flipped_horizontal is not None:
                # Save flipped image
                flipped_image_name = f"{base_name}_h_flip{file_extension}"
                flipped_image_path = os.path.join(output_folder, flipped_image_name)
                cv2.imwrite(flipped_image_path, img_flipped_horizontal)
                
                # Process and save flipped labels
                flipped_labels_path = os.path.join(output_folder, f"{base_name}_h_flip.txt")
                with open(flipped_labels_path, 'w') as f:
                    for label in labels:
                        class_id, x_center, y_center, width, height = label
                        new_class_id, new_x_center, new_y_center, new_width, new_height = flip_yolo_coordinates(
                            class_id, x_center, y_center, width, height, 'h'
                        )
                        f.write(f"{new_class_id} {new_x_center:.6f} {new_y_center:.6f} {new_width:.6f} {new_height:.6f}\n")

        # Process vertical flip
        if "_v_flip" not in image_name:
            img_flipped_vertical = cv2.flip(img, 0)
            
            if img_flipped_vertical is not None:
                # Save flipped image
                flipped_image_name = f"{base_name}_v_flip{file_extension}"
                flipped_image_path = os.path.join(output_folder, flipped_image_name)
                cv2.imwrite(flipped_image_path, img_flipped_vertical)
                
                # Process and save flipped labels
                flipped_labels_path = os.path.join(output_folder, f"{base_name}_v_flip.txt")
                with open(flipped_labels_path, 'w') as f:
                    for label in labels:
                        class_id, x_center, y_center, width, height = label
                        new_class_id, new_x_center, new_y_center, new_width, new_height = flip_yolo_coordinates(
                            class_id, x_center, y_center, width, height, 'v'
                        )
                        f.write(f"{new_class_id} {new_x_center:.6f} {new_y_center:.6f} {new_width:.6f} {new_height:.6f}\n")

        # Process horizontal + vertical flip
        if "_hv_flip" not in image_name:
            img_flipped_hv = cv2.flip(img, -1)
            
            if img_flipped_hv is not None:
                # Save flipped image
                flipped_image_name = f"{base_name}_hv_flip{file_extension}"
                flipped_image_path = os.path.join(output_folder, flipped_image_name)
                cv2.imwrite(flipped_image_path, img_flipped_hv)
                
                # Process and save flipped labels
                flipped_labels_path = os.path.join(output_folder, f"{base_name}_hv_flip.txt")
                with open(flipped_labels_path, 'w') as f:
                    for label in labels:
                        class_id, x_center, y_center, width, height = label
                        new_class_id, new_x_center, new_y_center, new_width, new_height = flip_yolo_coordinates(
                            class_id, x_center, y_center, width, height, 'hv'
                        )
                        f.write(f"{new_class_id} {new_x_center:.6f} {new_y_center:.6f} {new_width:.6f} {new_height:.6f}\n")

    except Exception as e:
        print(f"Error processing {image_name}: {e}")

def run_another_script(input_folder):
    """Run another Python script with --source argument (optional)"""
    script_path = "rename_new_format.py"  # Replace with the actual path to your script
    if os.path.exists(script_path):
        subprocess.run(["python", script_path, "--source", input_folder])
    else:
        print(f"Script {script_path} not found, skipping...")

def flip_images_and_labels(input_folder, label_folder=None, output_folder=None):
    """Main function to flip images and labels"""
    label_folder = label_folder or input_folder
    output_folder = output_folder or input_folder

    total_images = 0

    # Calculate the total number of ORIGINAL images (excluding already flipped ones)
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                # Only count original images, not flipped ones
                if not any(suffix in file for suffix in ['_h_flip', '_v_flip', '_hv_flip']):
                    total_images += 1

    os.makedirs(output_folder, exist_ok=True)

    # Initialize the progress bar with the total number of images
    pbar = tqdm(total=total_images, desc="Processing images", unit="image")

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                continue
            
            # Skip already flipped images - only process original images
            if any(suffix in file for suffix in ['_h_flip', '_v_flip', '_hv_flip']):
                continue  # Don't update progress for skipped flipped images
            
            # Use the file name directly, not the full path
            process_image_and_label(file, root, label_folder, output_folder)
            pbar.update(1)  # Update progress AFTER all 3 flips are completed for this image

    pbar.close()  # Close the progress bar when all images are processed

def parse_args():
    parser = argparse.ArgumentParser(description='Flip images and YOLO labels horizontally, vertically, and horizontally+vertically')
    parser.add_argument('--input_folder', required=True, help='Path to the folder containing input images')
    parser.add_argument('--label_folder', help='Path to the folder containing label files (default: same as input_folder)')
    parser.add_argument('--output_folder', help='Path to the folder where flipped images and labels will be saved (default: same as input_folder)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Optional: run another script first
    # run_another_script(args.input_folder)
    
    flip_images_and_labels(args.input_folder, args.label_folder, args.output_folder)