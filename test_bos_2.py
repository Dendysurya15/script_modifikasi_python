from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO
import os
from glob import glob
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import date
import shutil

# Define class mapping
class_mapping = {0: "normal", 1: "abnormal"}

# Input directory containing images
image_directory = "/home/grading/test/"

# Output directory for annotated images and XML annotations
output_directory = "/home/grading/test/new/"
os.makedirs(output_directory, exist_ok=True)

# Initialize YOLO model
conf = 0.5  # confidence threshold
iou = 0.45  # IoU threshold
imgsz = 640  # image size
max_det = 1000  # maximum detections
model = YOLO("/home/grading/yolov8/2024-05-27-14-21_yolov5su_1280_48_foto_mei/train/weights/best.pt")


# Define image extensions
image_extensions = ["*.jpg", "*.jpeg", "*.png"]
image_files = []

# Collect image paths
for ext in image_extensions:
    image_files.extend(glob(os.path.join(image_directory, ext)))

# Sort image files
image_files = sorted(image_files)

# Loop through image files
for image_path in image_files:
    # Load image
    frame = cv2.imread(image_path)
    image_filename = os.path.basename(image_path)

    results = model.predict(frame, conf=conf, iou=iou, imgsz=imgsz, max_det=max_det)
    boxes = results[0].boxes.xywh.cpu()
    try:
        track_ids = results[0].boxes.id.int().cpu().tolist()
    except Exception as e:
        track_ids = []
    clss = results[0].boxes.cls.cpu().tolist()

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Calculate the middle y-coordinate of the frame
    annotation = ET.Element("annotation")

    folder = ET.SubElement(annotation, "folder").text = "your_folder_name"
    filename = ET.SubElement(annotation, "filename").text = "your_image_filename.jpg"
    path = ET.SubElement(annotation, "path").text = "path/to/your/image.jpg"

    source = ET.SubElement(annotation, "source")
    ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(annotation, "size")
    ET.SubElement(size, "width").text = str(frame.shape[1])
    ET.SubElement(size, "height").text = str(frame.shape[0])
    ET.SubElement(size, "depth").text = str(frame.shape[2])

    segmented = ET.SubElement(annotation, "segmented").text = "0"
    for obj_box, obj_track_id, obj_cl in zip(boxes, track_ids, clss):
        class_label = class_mapping.get(int(obj_cl))
        obj_x, obj_y, obj_w, obj_h = obj_box

        xmin = max(0, int(obj_x - obj_w/ 2))
        ymin = max(0, int(obj_y - obj_h/ 2))
        xmax = min(frame.shape[1], int(obj_x + obj_w/ 2))
        ymax = min(frame.shape[0], int(obj_y+ obj_h / 2))
        # Create object element for each detected object
        object_elem = ET.SubElement(annotation, "object")
        ET.SubElement(object_elem, "name").text = class_label  # You may replace this with obj_cl
        ET.SubElement(object_elem, "pose").text = "Unspecified"
        ET.SubElement(object_elem, "truncated").text = "0"
        ET.SubElement(object_elem, "difficult").text = "0"

        bndbox = ET.SubElement(object_elem, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(xmin)
        ET.SubElement(bndbox, "ymin").text = str(ymin)
        ET.SubElement(bndbox, "xmax").text = str(xmax)
        ET.SubElement(bndbox, "ymax").text = str(ymax)

    dt = date.today()
    filename_wo_ext, _ = os.path.splitext(image_filename)
    xml_filename = os.path.join(output_directory, f"{filename_wo_ext}.xml")
    xml_string = minidom.parseString(ET.tostring(annotation)).toprettyxml(indent="    ")
    with open(xml_filename, "w") as f:
        f.write(xml_string)
        
    # Display the annotated frame
    cv2.imshow("YOLOv8", annotated_frame)

    # Save the annotated frame as a JPEG image
    output_path = os.path.join(output_directory, f"{image_filename}")
    print(output_path)
    print(image_path)
    #cv2.imwrite(output_path, frame)
    shutil.copy(image_path,output_path)

cv2.destroyAllWindows()
