import os
import shutil
import argparse

def compare_and_move_files(folder_origin, folder_compare, folder_output):
    # Get list of files in the origin and compare folders
    origin_files = set(os.listdir(folder_origin))
    compare_files = set(os.listdir(folder_compare))

    # Find files that are in the compare folder but not in the origin folder
    files_to_move = compare_files - origin_files

    # Create the output folder if it doesn't exist
    if not os.path.exists(folder_output):
        os.makedirs(folder_output)

    # Move the files
    for file_name in files_to_move:
        src_path = os.path.join(folder_compare, file_name)
        dest_path = os.path.join(folder_output, file_name)
        shutil.move(src_path, dest_path)
        print(f"Moved {file_name} to {folder_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare files between two folders and move non-matching files to output folder.")
    parser.add_argument('--folder_origin', required=True, help="Path to the origin folder")
    parser.add_argument('--folder_compare', required=True, help="Path to the compare folder")
    parser.add_argument('--folder_output', required=True, help="Path to the output folder")

    args = parser.parse_args()
    
    compare_and_move_files(args.folder_origin, args.folder_compare, args.folder_output)
