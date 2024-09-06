import os
import argparse
from tqdm import tqdm
import time

def find_specific_class(folder_path, class_name, output_file):
    # List all files in the folder and its subfolders
    label_files = [f for f in get_all_files(folder_path) if f.endswith('.txt')]

    # Open the output file in write mode
    with open(output_file, 'w') as output:
        # Iterate through each label file using tqdm for progress bar
        for label_file in tqdm(label_files, desc="Searching", unit="file"):
            with open(label_file, 'r') as file:
                lines = file.readlines()
                # Iterate through each line in the label file
                for line in lines:
                    # Split the line into components (class, x_center, y_center, width, height)
                    components = line.strip().split()
                    if components:
                        # Check if the class is the one you are looking for
                        if int(components[0]) == class_name:
                            output.write(f"Found class {class_name} in file: {label_file}\n")
                            output.write(f"Details: {components[1:]}\n\n")

def get_all_files(folder_path):
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files

def main():
    parser = argparse.ArgumentParser(description='Find a specific class in YOLOv8 label files.')
    parser.add_argument('--input', type=str, help='Path to the labels folder')
    parser.add_argument('--cls', type=int, help='Class to find in the labels')
    parser.add_argument('--output', type=str, default='output.txt', help='Output file to store results')

    args = parser.parse_args()

    start_time = time.time()
    find_specific_class(args.input, args.cls, args.output)
    end_time = time.time()

    print(f"Search completed. Results written to {args.output}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
