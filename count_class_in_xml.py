import os
import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict

def count_name_classes_in_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    name_counts = defaultdict(int)
    
    for obj in root.findall('object'):
        name = obj.find('name').text
        if name:
            name_counts[name] += 1
            
    return name_counts

def main():
    parser = argparse.ArgumentParser(description="Count occurrences of each class name in XML files.")
    parser.add_argument('--folder', type=str, help="Folder containing XML files.")
    args = parser.parse_args()

    folder = args.folder

    if not os.path.isdir(folder):
        print(f"Error: {folder} is not a valid directory.")
        return

    xml_files = [f for f in os.listdir(folder) if f.endswith('.xml')]
    if not xml_files:
        print(f"No XML files found in directory: {folder}")
        return

    for xml_file in xml_files:
        file_path = os.path.join(folder, xml_file)
        name_counts = count_name_classes_in_file(file_path)
        
        counts_str = ', '.join([f"'{name}' Count: {count}" for name, count in name_counts.items()])
        print(f"File: {xml_file}, {counts_str}")

if __name__ == "__main__":
    main()
