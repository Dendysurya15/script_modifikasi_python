import os
import random
import shutil
import argparse

def create_folders(output_folder):
    train_folder = os.path.join(output_folder, 'train')
    val_folder = os.path.join(output_folder, 'val')
    
    print(f"Creating folders: {train_folder}, {val_folder}")  # Add this line
    
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)

    return train_folder, val_folder

def get_file_pairs(source_folder):
    files = os.listdir(source_folder)
    image_exts = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    img_files = [f for f in files if f.endswith(image_exts)]
    xml_files = set(f for f in files if f.endswith('.xml'))
    txt_files = set(f for f in files if f.endswith('.txt'))

    file_pairs = []
    for img_file in img_files:
        base_name = os.path.splitext(img_file)[0]
        xml_file = base_name + '.xml'
        txt_file = base_name + '.txt'

        pair = {
            "image": img_file,
            "xml": xml_file if xml_file in xml_files else None,
            "txt": txt_file if txt_file in txt_files else None
        }

        file_pairs.append(pair)

    return file_pairs

def split_data(file_pairs, train_ratio=0.8):
    """
    Split data into train and validation sets.
    Default: 80% train, 20% validation
    """
    random.shuffle(file_pairs)
    split_index = int(len(file_pairs) * train_ratio)
    train_files = file_pairs[:split_index]
    val_files = file_pairs[split_index:]
    return train_files, val_files

def move_files(file_pairs, destination_folder, source_folder):
    for pair in file_pairs:
        shutil.move(os.path.join(source_folder, pair["image"]), os.path.join(destination_folder, pair["image"]))
        if pair["xml"]:
            shutil.move(os.path.join(source_folder, pair["xml"]), os.path.join(destination_folder, pair["xml"]))
        if pair["txt"]:
            shutil.move(os.path.join(source_folder, pair["txt"]), os.path.join(destination_folder, pair["txt"]))

def main(input_folder, output_folder, train_ratio=0.8):
    create_folders(output_folder)
    file_pairs = get_file_pairs(input_folder)
    
    if len(file_pairs) == 0:
        print("No image files found in the input folder!")
        return
    
    train_files, val_files = split_data(file_pairs, train_ratio)
    move_files(train_files, os.path.join(output_folder, 'train'), input_folder)
    move_files(val_files, os.path.join(output_folder, 'val'), input_folder)
    
    print(f"Successfully split {len(file_pairs)} file pairs:")
    print(f"  - {len(train_files)} pairs moved to 'train' folder ({train_ratio*100:.0f}%)")
    print(f"  - {len(val_files)} pairs moved to 'val' folder ({(1-train_ratio)*100:.0f}%)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split image, XML, and TXT files into training and validation sets.")
    parser.add_argument('--i', '--input', required=True, help="Input folder containing the image, XML, and TXT files.", dest='i')
    parser.add_argument('--o', '--output', required=True, help="Output folder where 'train' and 'val' folders will be created.", dest='o')
    parser.add_argument('--ratio', type=float, default=0.8, help="Training ratio (default: 0.8 for 80% train, 20% val)")
    
    args = parser.parse_args()
    
    if args.ratio <= 0 or args.ratio >= 1:
        print("Error: Training ratio must be between 0 and 1")
        exit(1)
    
    main(args.i, args.o, args.ratio)