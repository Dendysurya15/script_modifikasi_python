import os
import argparse

def convert_labels(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Iterate through each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(input_folder, filename), 'r') as f:
                lines = f.readlines()
                # Modify the label for each line
                modified_lines = ['0 ' + line.split(' ', 1)[1] for line in lines]
            # Write the modified lines to a new file in the output folder
            with open(os.path.join(output_folder, filename), 'w') as f:
                f.writelines(modified_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert YOLO labels to 0')
    parser.add_argument('--input_folder', type=str, help='Path to the folder containing YOLO txt files')
    parser.add_argument('--output_folder', type=str, help='Path to the folder to store modified YOLO txt files')
    args = parser.parse_args()
    
    convert_labels(args.input_folder, args.output_folder)
