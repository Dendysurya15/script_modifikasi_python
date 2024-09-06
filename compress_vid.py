import argparse
import os
from moviepy.editor import VideoFileClip

def compress_and_convert_to_mkv(input_file, output_folder, bitrate='1M'):
    output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file))[0] + '.mkv')
    try:
        clip = VideoFileClip(input_file)
        clip.write_videofile(output_file, codec='libx264', bitrate=bitrate, audio_codec='aac')
        print(f"Video has been successfully compressed and converted to {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compress and convert video to MKV format.')
    parser.add_argument('--i', dest='input_file', required=True, help='Input video file path (MPEG-4 format)')
    parser.add_argument('--o', dest='output_folder', required=True, help='Output folder directory for the converted video')
    args = parser.parse_args()
    
    compress_and_convert_to_mkv(args.input_file, args.output_folder)
