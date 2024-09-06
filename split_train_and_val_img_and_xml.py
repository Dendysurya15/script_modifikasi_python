import os
import random
import shutil
import argparse

def create_folders(output_folder):
    train_folder = os.path.join(output_folder, 'train')
    val_folder = os.path.join(output_folder, 'val')
    
    if not os.path.exists(train_folder):
        os.makedirs(train_folder)
    if not os.path.exists(val_folder):
        os.makedirs(val_folder)

    return train_folder, val_folder

def get_file_pairs(source_folder):
    files = os.listdir(source_folder)
    img_files = [f for f in files if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.jpeg') or f.endswith('.JPG') or f.endswith('.JPEG') or f.endswith('.PNG')]  # Add other image file extensions if needed
    xml_files = [f for f in files if f.endswith('.xml')]

    file_pairs = []
    for img_file in img_files:
        base_name = os.path.splitext(img_file)[0]
        corresponding_xml = base_name + '.xml'
        if corresponding_xml in xml_files:
            file_pairs.append((img_file, corresponding_xml))

    return file_pairs

def split_data(file_pairs, train_ratio=0.8):
    random.shuffle(file_pairs)
    split_index = int(len(file_pairs) * train_ratio)
    train_files = file_pairs[:split_index]
    val_files = file_pairs[split_index:]
    return train_files, val_files

def move_files(file_pairs, destination_folder, source_folder):
    for img_file, xml_file in file_pairs:
        shutil.move(os.path.join(source_folder, img_file), os.path.join(destination_folder, img_file))
        shutil.move(os.path.join(source_folder, xml_file), os.path.join(destination_folder, xml_file))

def main(input_folder, output_folder):
    create_folders(output_folder)
    file_pairs = get_file_pairs(input_folder)
    train_files, val_files = split_data(file_pairs)
    move_files(train_files, os.path.join(output_folder, 'train'), input_folder)
    move_files(val_files, os.path.join(output_folder, 'val'), input_folder)
    print(f"Moved {len(train_files)} pairs to 'train' and {len(val_files)} pairs to 'val'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split image and XML files into training and validation sets.")
    parser.add_argument('--i', '--input', required=True, help="Input folder containing the image and XML files.")
    parser.add_argument('--o', '--output', required=True, help="Output folder where 'train' and 'val' folders will be created.")
    
    args = parser.parse_args()
    
    main(args.i, args.o)
