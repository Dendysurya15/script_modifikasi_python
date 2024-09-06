import os
import shutil
import argparse
import random

def create_folders(output_folder):
    train_path = os.path.join(output_folder, 'train')
    val_path = os.path.join(output_folder, 'val')
    test_path = os.path.join(output_folder, 'test')
    
    os.makedirs(train_path, exist_ok=True)
    os.makedirs(val_path, exist_ok=True)
    os.makedirs(test_path, exist_ok=True)
    
    return train_path, val_path, test_path

def move_files(input_folder, train_path, val_path, test_path):
    files = os.listdir(input_folder)
    
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    txt_files = [f for f in files if f.lower().endswith('.txt')]
    
    paired_files = []
    for img in image_files:
        txt_file = img.rsplit('.', 1)[0] + '.txt'
        if txt_file in txt_files:
            paired_files.append((img, txt_file))
    
    random.shuffle(paired_files)
    
    train_size = int(0.7 * len(paired_files))
    val_size = int(0.15 * len(paired_files))
    
    train_files = paired_files[:train_size]
    val_files = paired_files[train_size:train_size + val_size]
    test_files = paired_files[train_size + val_size:]
    
    for img, txt in train_files:
        shutil.move(os.path.join(input_folder, img), os.path.join(train_path, img))
        shutil.move(os.path.join(input_folder, txt), os.path.join(train_path, txt))
        
    for img, txt in val_files:
        shutil.move(os.path.join(input_folder, img), os.path.join(val_path, img))
        shutil.move(os.path.join(input_folder, txt), os.path.join(val_path, txt))
        
    for img, txt in test_files:
        shutil.move(os.path.join(input_folder, img), os.path.join(test_path, img))
        shutil.move(os.path.join(input_folder, txt), os.path.join(test_path, txt))

def main():
    parser = argparse.ArgumentParser(description='Divide files into train, val, and test folders.')
    parser.add_argument('--input_folder', type=str, required=True, help='The input folder containing images and TXT files')
    parser.add_argument('--output_folder', type=str, required=True, help='The output folder where train, val, and test folders will be created')
    
    args = parser.parse_args()
    input_folder = args.input_folder
    output_folder = args.output_folder
    
    if not os.path.exists(input_folder):
        print(f"Error: The input folder '{input_folder}' does not exist.")
        return
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)
    
    train_path, val_path, test_path = create_folders(output_folder)
    move_files(input_folder, train_path, val_path, test_path)
    
    print('Files have been successfully moved.')

if __name__ == "__main__":
    main()
