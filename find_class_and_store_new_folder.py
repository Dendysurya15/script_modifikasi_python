import os
import shutil
import argparse
from xml.etree import ElementTree as ET

def find_files_by_class(src_folder, class_name, dest_folder):
    # Create the destination subfolder named after the class if it doesn't exist
    class_folder = os.path.join(dest_folder, class_name)
    os.makedirs(class_folder, exist_ok=True)
    
    # Iterate through all files in the source folder
    for filename in os.listdir(src_folder):
        if filename.endswith('.xml'):
            xml_path = os.path.join(src_folder, filename)
            # Parse the XML file
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Check if the class_name is in the XML file
            contains_class = any(class_name in element.text for element in root.iter() if element.tag == 'name')
            
            if contains_class:
                # Move the XML file to the destination class folder
                shutil.move(xml_path, os.path.join(class_folder, filename))
                
                # Move the corresponding image file(s) to the destination class folder
                image_extensions = ['.PNG','.JPG','.JPEG','.jpeg', '.jpg', '.png']
                base_filename = os.path.splitext(filename)[0]
                for ext in image_extensions:
                    image_path = os.path.join(src_folder, base_filename + ext)
                    if os.path.exists(image_path):
                        shutil.move(image_path, os.path.join(class_folder, base_filename + ext))

def main():
    parser = argparse.ArgumentParser(description='Organize files by XML content.')
    parser.add_argument('--src_folder', required=True, help='Source folder containing XML and image files.')
    parser.add_argument('--name_label', required=True, help='Class name to filter the files.')
    parser.add_argument('--dest_folder', required=True, help='Destination folder to move the filtered files.')

    args = parser.parse_args()
    
    find_files_by_class(args.src_folder, args.name_label, args.dest_folder)

if __name__ == '__main__':
    main()
