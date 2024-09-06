import os
import argparse

def rename_files(input_folder):
    all_files = os.listdir(os.path.abspath(input_folder))

    image_extensions = ['jpg', 'jpeg', 'png', 'gif']  # Add more extensions if needed

    for file_name in all_files:
        if file_name.count('.') == 2:
            base_name, extension = file_name.rsplit('.', 1)
            if extension.lower() in image_extensions:
                new_name = base_name.replace('.', '_', 1) + '.' + extension
                old_path = os.path.join(input_folder, file_name)
                new_path = os.path.join(input_folder, new_name)
                os.rename(old_path, new_path)
                print(f'Renamed: {file_name} to {new_name}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rename files with specific conditions.')
    parser.add_argument('--input_folder', type=str, help='Path to the input folder containing files')

    args = parser.parse_args()

    if args.input_folder:
        rename_files(args.input_folder)
    else:
        print("Please provide the --input_folder argument.")
