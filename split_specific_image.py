import os
import argparse
import shutil

def process_files(input_folder, output_folder):
    # List all files in the input folder
    files = os.listdir(input_folder)

    # Iterate through each file in the input folder
    for file in files:
        # Check if the file name contains ".mp4"
        if ".mp4" in file:
            # Create the full path for the input file
            input_file_path = os.path.join(input_folder, file)

            # Create the base name for the output files
            base_name, _ = os.path.splitext(file)

            # Create the full paths for the output files
            output_txt_path = os.path.join(output_folder, base_name + ".txt")
            output_xml_path = os.path.join(output_folder, base_name + ".xml")
            output_image_path = os.path.join(output_folder, base_name + ".JPG")

            # Move the files to the output folder
            shutil.move(input_file_path, output_txt_path)
            shutil.move(input_file_path, output_xml_path)
            shutil.move(input_file_path, output_image_path)

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Process files containing '.mp4' in the name.")
    parser.add_argument("--input_folder", required=True, help="Path to the input folder.")
    parser.add_argument("--output_folder", required=True, help="Path to the output folder.")

    # Parse command-line arguments
    args = parser.parse_args()

    # Process files based on input and output folders
    process_files(args.input_folder, args.output_folder)
