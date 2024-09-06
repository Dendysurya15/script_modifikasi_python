import argparse
import subprocess
from pathlib import Path
import os
from datetime import datetime

def get_video_files(folder_path):
    video_files = []
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.avi', '.mkv', '.mov', '.wmv']:
            video_files.append(str(file_path))
    return video_files

folder_split = Path(os.getcwd()) / 'folder_split'

# Make sure the directory exists
folder_split.mkdir(parents=True, exist_ok=True)

subdirectories = []

for item in folder_split.iterdir():
    if item.is_dir():
        try:
            datetime.strptime(item.name, "%Y-%m-%d")
            subdirectories.append(item)
        except ValueError:
            pass

for subdirectory in subdirectories:
    print(f"Processing videos in folder: {subdirectory}")

    videos_list = get_video_files(subdirectory)

    parser = argparse.ArgumentParser(description='Run Python code with multiple video sources.')
    parser.add_argument('--source', nargs='+', help='List of video sources.')
    args = parser.parse_args()

    if args.source:
        videos_list = args.source


    for video_source in videos_list:
        print(f"Processing video: {video_source}")
        subprocess.run(['python', 'convert_vid_to_img.py', '--source', video_source, '--yolo_model','/home/grading/yolov8/weight/training_14_desember_total/weights/best.pt'])
