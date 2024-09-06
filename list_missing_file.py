import os
import argparse

def list_missing_files(input_folder):
    missing_files = []
    
    for filename in os.listdir(input_folder):
        name, ext = os.path.splitext(filename)
        
        if ext == '.jpg':
            xml_path = os.path.join(input_folder, f"{name}.xml")
            
            if not os.path.exists(xml_path):
                missing_files.append(filename)

    return missing_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List jpg files without corresponding xml files.")
    parser.add_argument("--input_folder", type=str, help="Path to the input folder containing jpg files.")
    args = parser.parse_args()

    if args.input_folder:
        missing_files = list_missing_files(args.input_folder)

        if missing_files:
            print("Jpg files without corresponding xml files:")
            for file in missing_files:
                print(file)
        else:
            print("All jpg files have corresponding xml files.")
    else:
        print("Please provide the --input_folder argument.")
