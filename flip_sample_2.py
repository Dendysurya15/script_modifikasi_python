import cv2
import os
import xml.etree.ElementTree as ET
import argparse
from tqdm import tqdm
import threading
import subprocess

def is_valid_xml_file(file_path):
    try:
        ET.parse(file_path)
        return True
    except ET.ParseError:
        return False

def process_image_and_label(image_name, input_folder, label_folder, output_folder, flip):
    # Replace invalid characters in the file name
    image_name_original = image_name

    # Construct paths using os.path.join for cross-platform compatibility
    image_path = os.path.join(input_folder, image_name)

    # Check if the image file exists
    if not os.path.isfile(image_path):
        print(f"Skipping non-existent image: {image_path}")
        return

    # Correctly generate label file name
    label_file_name = os.path.splitext(image_name)[0] + '.xml'
    label_path = os.path.join(label_folder, label_file_name)

    # Check if the XML file is well-formed
    if not is_valid_xml_file(label_path):
        print(f"Skipping invalid XML file: {image_name_original}")
        return

    print(f"Processing image: {image_path}")

    try:
        # Read image
        img = cv2.imread(image_path)

        # Check if the image is successfully loaded
        if img is None:
            #print(f"Error: Unable to read image file: {image_path}")
            return


        # Read and flip labels
        tree = ET.parse(label_path)
        root = tree.getroot()
        # Flip image horizontally if not already flipped
        if flip == 'h':
            img_flipped_horizontal = cv2.flip(img, 1)

            if not img_flipped_horizontal.any():
                print(f"Warning: Flipped image is empty for {image_path}")
            else:
                test = os.path.join(output_folder, f"{image_name.replace(os.path.splitext(image_name)[1], '_h_flip.jpg')}")
                cv2.imwrite(test, img_flipped_horizontal)

            for obj in root.findall('.//object'):
                xmin = int(obj.find('bndbox/xmin').text)
                ymin = int(obj.find('bndbox/ymin').text)
                xmax = int(obj.find('bndbox/xmax').text)
                ymax = int(obj.find('bndbox/ymax').text)

                xmin_flipped = img.shape[1] - xmax
                xmax_flipped = img.shape[1] - xmin
                ymin_flipped = ymin
                ymax_flipped = ymax

                obj.find('bndbox/xmin').text = str(xmin_flipped)
                obj.find('bndbox/xmax').text = str(xmax_flipped)
                obj.find('bndbox/ymin').text = str(ymin_flipped)
                obj.find('bndbox/ymax').text = str(ymax_flipped)

            output_path_h = os.path.join(output_folder, f"{image_name.replace(os.path.splitext(image_name)[1], '_h_flip.xml')}")
            tree.write(output_path_h)

        # Flip image vertically if not already flipped
        if flip == 'v':
            img_flipped_vertical = cv2.flip(img, 0)

            if not img_flipped_vertical.any():
                print(f"Warning: Flipped image is empty for {image_path}")
            else:
                
                cv2.imwrite(os.path.join(output_folder, f"{image_name.replace(os.path.splitext(image_name)[1], '_v_flip.jpg')}"), img_flipped_vertical)

            for obj in root.findall('.//object'):
                xmin = int(obj.find('bndbox/xmin').text)
                ymin = int(obj.find('bndbox/ymin').text)
                xmax = int(obj.find('bndbox/xmax').text)
                ymax = int(obj.find('bndbox/ymax').text)

                xmin_flipped = img.shape[1] - xmin
                xmax_flipped = img.shape[1] - xmax
                ymin_flipped = img.shape[0] - ymax
                ymax_flipped = img.shape[0] - ymin

                obj.find('bndbox/xmin').text = str(xmin_flipped)
                obj.find('bndbox/xmax').text = str(xmax_flipped)
                obj.find('bndbox/ymin').text = str(ymin_flipped)
                obj.find('bndbox/ymax').text = str(ymax_flipped)

            output_path_v = os.path.join(output_folder, f"{image_name.replace(os.path.splitext(image_name)[1], '_v_flip.xml')}")
            tree.write(output_path_v)

        # Flip image horizontally+vertically if not already flipped
        if flip == 'hv':
            img_flipped_hv = cv2.flip(img, -1)

            if not img_flipped_hv.any():
                print(f"Warning: Flipped image is empty for {image_path}")
            else:
                cv2.imwrite(os.path.join(output_folder, f"{image_name.replace(os.path.splitext(image_name)[1], '_hv_flip.jpg')}"), img_flipped_hv)
            
            for obj in root.findall('.//object'):
                xmin = int(obj.find('bndbox/xmin').text)
                ymin = int(obj.find('bndbox/ymin').text)
                xmax = int(obj.find('bndbox/xmax').text)
                ymax = int(obj.find('bndbox/ymax').text)

                xmin_flipped = img.shape[1] - xmax
                xmax_flipped = img.shape[1] - xmin
                ymin_flipped = ymax
                ymax_flipped = ymin

                obj.find('bndbox/xmin').text = str(xmin_flipped)
                obj.find('bndbox/xmax').text = str(xmax_flipped)
                obj.find('bndbox/ymin').text = str(ymin_flipped)
                obj.find('bndbox/ymax').text = str(ymax_flipped)

            output_path_hv = os.path.join(output_folder, f"{image_name.replace(os.path.splitext(image_name)[1], '_hv_flip.xml')}")
            tree.write(output_path_hv)

    except ET.ParseError:
        print(f"Error parsing XML file: {label_path}. Skipping this file.")

def run_another_script(input_folder):
    # Run another Python script with --source argument
    script_path = "rename_new_format.py"  # Replace with the actual path to your script
    subprocess.run(["python", script_path, "--source", input_folder])

def flip_images_and_labels(input_folder, label_folder=None, output_folder=None):
    label_folder = label_folder or input_folder
    output_folder = output_folder or input_folder

    # threading.Thread(target=run_another_script, args=(input_folder,)).start()
    total_images = 0

    # Calculate the total number of images

    os.makedirs(output_folder, exist_ok=True)

    # Initialize the progress bar with the total number of images
    hflippeds = []
    hvflippeds = []
    vflippeds = []
    not_flippeds = []
    root_folder = ''
    for root,dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)

            
            if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                continue
            if '_h_flip' in file:
                hflippeds.append(file.lower())
            elif '_hv_flip' in file:
                hvflippeds.append(file.lower())
            elif '_v_flip' in file:
                vflippeds.append(file.lower())
            else:
                not_flippeds.append(file_path)
            total_images += 1
        
        root_folder = root

    pbar = tqdm(total=total_images, desc="Processing images", unit="image")

    
    for not_flipped in not_flippeds:
        file_not_flipped = os.path.basename(not_flipped)
        fileNa, extension = os.path.splitext(file_not_flipped)
        if file_not_flipped.replace(extension, '_h_flip' + extension).lower() not in hflippeds:
            process_image_and_label(not_flipped, root_folder, label_folder, output_folder,'h')
        if file_not_flipped.replace(extension, '_v_flip' + extension).lower() not in vflippeds:
            process_image_and_label(not_flipped, root_folder, label_folder, output_folder,'v')
        if file_not_flipped.replace(extension, '_hv_flip' + extension).lower() not in hvflippeds:
            process_image_and_label(not_flipped, root_folder, label_folder, output_folder,'hv')
        pbar.update(1)  # Update the progress bar for each processed image
    pbar.close()  # Close the progress bar when all images are processed

def parse_args():
    parser = argparse.ArgumentParser(description='Flip images and labels horizontally, vertically, and horizontally+vertically')
    parser.add_argument('--input_folder', required=True, help='Path to the folder containing input images')
    parser.add_argument('--label_folder', help='Path to the folder containing label files (default: same as input_folder)')
    parser.add_argument('--output_folder', help='Path to the folder where flipped images and labels will be saved (default: same as input_folder)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_another_script(args.input_folder)
    flip_images_and_labels(args.input_folder, args.label_folder, args.output_folder)
