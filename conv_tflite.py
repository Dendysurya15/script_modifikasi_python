# from ultralytics import YOLO
# model = YOLO("best.pt")
# model.export(format="tflite")

import argparse
from os.path import join
from ultralytics import YOLO

def main(args):
    model_path = join(args.path, args.model)
    model = YOLO(model_path)
    model.export(format="tflite")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export YOLO model to TensorFlow Lite")
    parser.add_argument("--path", type=str, required=True, help="Path to the model directory")
    parser.add_argument("--model", type=str, default="best.pt", help="Model filename (default: best.pt)")
    args = parser.parse_args()
    main(args)