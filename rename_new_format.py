import os
import argparse
import re
import xml.etree.ElementTree as ET

def get_file_list(source_directory):
    file_list = []
    try:
        # Get the list of files in the specified directory
        file_list = os.listdir(source_directory)
    except FileNotFoundError:
        print(f"Error: The specified directory '{source_directory}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied for the directory '{source_directory}'.")
    return file_list

def list_xml_files(source_directory, full_with_extension=False):
    if full_with_extension:
        xml_files = [file for file in os.listdir(source_directory) if file.lower().endswith('.xml')]
    else:
        xml_files = [os.path.splitext(file)[0] for file in os.listdir(source_directory) if file.lower().endswith('.xml')]
    return xml_files

def update_xml_file(xml_file_path, xml_file_original):
    try:
        # Parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Specify the original filename without the extension
        original_filename = xml_file_original


        print(root.iter())
        for elem in root.iter():   
            print(original_filename)
            print(elem.text)
            
            if original_filename == elem.text:
                elem.text = elem.text.replace('_h', '')
            elif original_filename in str(elem.text):
                print('ada bos')
                # Replace dots with underscores in the filename part
                filename, extension = os.path.splitext(elem.text)
                
                name_file = filename
                new_filename = name_file.replace('_h', '')
                
                new_content = new_filename + extension.lower()
                elem.text = new_content

        # Save the modified content back to the file
        tree.write(xml_file_path)

        # print(xml_file_path)
        # print(f"Updated XML file: {xml_file_path}")

    except ET.ParseError:
        print(f"Error parsing XML file: {xml_file_path}")
        
def filter_and_rename_files(file_list, source_directory):

    
    for file in file_list:
        if file.count('.') > 1:

            print(file)
            # Split the filename and extension
            filename, extension = os.path.splitext(file)
            
            # Replace dots with underscores in the filename only
            new_filename = filename.replace('_h', '')
            
            # Combine the new filename with the original extension
            new_name = new_filename + extension.lower()
            
            old_path = os.path.join(source_directory, file)
            new_path = os.path.join(source_directory, new_name)
            
            # Rename the file
            os.rename(old_path, new_path)
            # print(f"Renamed: {file} to {new_name}")


def natural_sort_key(filename):
    # Extract numeric part from the filename
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', filename)]           

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="List files in a specified directory.")

    # Add the --source argument
    parser.add_argument("--source", help="Specify the source directory path", required=True)

    # Parse the command-line arguments
    args = parser.parse_args()

    # Get the list of files in the specified directory
    source_directory = args.source
    file_list = get_file_list(source_directory)

    xml_files_original = list_xml_files(source_directory ,False)
    xml_files_original_sorted = sorted(xml_files_original, key=natural_sort_key)
    
    filter_and_rename_files(file_list, source_directory)

    # xml_files = list_xml_files(source_directory, True)
    # xml_files_sorted = sorted(xml_files, key=natural_sort_key)

    
    # if xml_files:
    #     for xml_file, xml_file_original in zip(xml_files_sorted, xml_files_original_sorted):
    #         update_xml_file(os.path.join(source_directory, xml_file),xml_file_original)
    # else:
    #     print("\nNo XML files found in the specified directory.")

if __name__ == "__main__":
    main()
