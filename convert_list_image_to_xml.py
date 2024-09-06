from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO
import os
from glob import glob
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from datetime import date
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, default='', help='model.pt path')
opt = parser.parse_args()
source = opt.source
image_directory = source

current_directory = os.getcwd()
output_directory = os.path.join(current_directory, "auto_labelling_img")

if not os.path.exists(output_directory):
    os.makedirs(output_directory)
    print(f"Directory '{output_directory}' created successfully.")

image_extensions = ["*.jpg", "*.png", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]
image_files = []


for ext in image_extensions:
    image_files.extend(glob(os.path.join(image_directory, ext)))

image_files = sorted(image_files)

# class_mapping = {
#     0: "unripe",
#     1: "ripe",
#     2: "overripe",
#     3: "empty_bunch",
#     4: "abnormal"
# }
class_mapping ={
    0 : "normal",
    1 : "abnormal"
}
# class_mapping = {
#     0: 'adoretus_dewasa',
#     1: 'amathusia_dewasa',
#     2: 'amathusia_larva',
#     3: 'amathusia_pupa',
#     4: 'ambadra_dewasa',
#     5: 'aphis_sp_dewasa',
#     6: 'aphis_sp_telur',
#     7: 'birthamula_dewasa',
#     8: 'birthamula_larva',
#     9: 'birthosea_bisura_larva',
#     10: 'calliteara_dewasa',
#     11: 'calliteara_telur',
#     12: 'dasychira_mendosa_dewasa',
#     13: 'dasychira_mendosa_larva',
#     14: 'dasychira_mendosa_pupa',
#     15: 'dasychira_mendosa_telur',
#     16: 'helopeltis_dewasa',
#     17: 'helopeltis_nymph',
#     18: 'locusta_migratoria_dewasa',
#     19: 'locusta_migratoria_nymph',
#     20: 'oryctes_rhinoceros_dewasa',
#     21: 'parasa_lepida_larva',
#     22: 'rhabdoscelus_dewasa',
#     23: 'rhynchophorus_dewasa',
#     24: 'spodoptera_litura_dewasa',
#     25: 'valanga_nigricornis_dewasa'
# }


for image_path in image_files:
    
    file_name, _ = os.path.splitext(os.path.basename(image_path))
    # Load the YOLOv8 model
    model = YOLO("/home/grading/yolov8/2024-05-27-14-21_yolov5su_1280_48_foto_mei/train/weights/best.pt")

    cap = cv2.VideoCapture(image_path)

    # Store the track history
    track_history = defaultdict(lambda: [])

    # Initialize variables for counting

    # Loop through the video frames
    frame_count = 0  # Counter for saving frames

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break

        results = model.track(frame, persist=True, conf=0.01, iou=0.5, imgsz=1280, max_det=12000)


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
        
        xml_filename = os.path.join(output_directory, f"{dt}_{file_name}.xml")
        xml_string = minidom.parseString(ET.tostring(annotation)).toprettyxml(indent="    ")
        with open(xml_filename, "w") as f:
            f.write(xml_string)
            
      
        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        # Save the annotated frame as a JPEG image
        frame_count += 1
        output_path = os.path.join(output_directory, f"{dt}_{file_name}{os.path.splitext(image_path)[-1]}")
        cv2.imwrite(output_path, frame)

        

    
        cv2.waitKey(30)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()

