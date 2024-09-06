import argparse
import os
import shutil

def copy_files(input_txt, input_folder, output_folder):
    with open(input_txt, 'r') as file_list:
        for line in file_list:
            file_name = line.strip()

            if ".txt" in file_name:
                # print(f"Skipping file '{file_name}' as it contains '_h_flip', '_v_flip', or '_hv_flip'.")
                # continue
                source_path = os.path.join(input_folder, file_name)
                destination_path = os.path.join(output_folder, file_name)
            else:
                continue
            
            try:
                shutil.move(source_path, destination_path)
                print(f"File '{file_name}' copied successfully to '{output_folder}'.")
            except FileNotFoundError:
                print(f"File '{file_name}' not found in the source folder.")
            except PermissionError:
                print(f"Permission error: Unable to copy '{file_name}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy files listed in a text file from source folder to destination folder.")
    parser.add_argument("--input_txt", required=True, help="Path to the text file containing file names to be copied.")
    parser.add_argument("--input_folder", required=True, help="Path to the source folder.")
    parser.add_argument("--output_folder", required=True, help="Path to the destination folder.")

    args = parser.parse_args()
    copy_files(args.input_txt, args.input_folder, args.output_folder)
