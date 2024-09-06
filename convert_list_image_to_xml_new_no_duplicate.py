import os
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from PIL import Image
from ultralytics import YOLO
import argparse
import torch

class_mapping = {
    0: "abnormal",
    1: "normal"
}

def create_voc_xml(image_path, boxes, output_folder, clss):
    image_name = os.path.basename(image_path)
    image_name_no_ext = os.path.splitext(image_name)[0]
    
    with Image.open(image_path) as img:
        width, height = img.size

    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = os.path.basename(output_folder)
    ET.SubElement(annotation, 'filename').text = image_name
    ET.SubElement(annotation, 'path').text = image_path

    source = ET.SubElement(annotation, 'source')
    ET.SubElement(source, 'database').text = 'Unknown'

    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = str(width)
    ET.SubElement(size, 'height').text = str(height)
    ET.SubElement(size, 'depth').text = str(3)

    ET.SubElement(annotation, 'segmented').text = str(0)

    for box, obj_cl in zip(boxes, clss):
        class_label = class_mapping.get(int(obj_cl))
        obj = ET.SubElement(annotation, 'object')
        ET.SubElement(obj, 'name').text = class_label
        ET.SubElement(obj, 'pose').text = 'Unspecified'
        ET.SubElement(obj, 'truncated').text = str(0)
        ET.SubElement(obj, 'difficult').text = str(0)
        bndbox = ET.SubElement(obj, 'bndbox')
        ET.SubElement(bndbox, 'xmin').text = str(int(box[0]))
        ET.SubElement(bndbox, 'ymin').text = str(int(box[1]))
        ET.SubElement(bndbox, 'xmax').text = str(int(box[2]))
        ET.SubElement(bndbox, 'ymax').text = str(int(box[3]))

    xml_str = ET.tostring(annotation)
    parsed_xml = parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")

    xml_file_path = os.path.join(output_folder, f"{image_name_no_ext}.xml")
    with open(xml_file_path, 'w') as f:
        f.write(pretty_xml)

def non_max_suppression(boxes, scores, iou_threshold):
    keep = []
    if len(boxes) == 0:
        return keep

    indices = torch.argsort(scores, descending=True)
    while indices.numel() > 0:
        current = indices[0]
        keep.append(current.item())
        if indices.numel() == 1:
            break
        current_box = boxes[current].unsqueeze(0)
        other_boxes = boxes[indices[1:]]
        ious = box_iou(current_box, other_boxes)
        indices = indices[1:][ious <= iou_threshold]

    return keep

def box_iou(box1, box2):
    inter = (torch.min(box1[:, 2], box2[:, 2]) - torch.max(box1[:, 0], box2[:, 0])).clamp(0) * \
            (torch.min(box1[:, 3], box2[:, 3]) - torch.max(box1[:, 1], box2[:, 1])).clamp(0)
    area1 = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])
    area2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])
    union = area1 + area2 - inter
    return inter / union

def main():
    parser = argparse.ArgumentParser(description="Process images and generate VOC XML annotations.")
    parser.add_argument('--source', type=str, required=True, help="Path to the folder containing images")
    parser.add_argument('--model', type=str, required=True, help="Path to the YOLO model")
    args = parser.parse_args()

    model = YOLO(args.model)

    folder_path = args.source
    image_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".jpg") or file.endswith(".tif")]

    results = model.predict(image_files, conf=0.01, iou=0.12, imgsz=11000, max_det=12000)

    for image_path, result in zip(image_files, results):
        clss = result.boxes.cls.cpu().tolist()
        boxes = result.boxes.xyxy.cpu()
        scores = result.boxes.conf.cpu()

        # Apply Non-Maximum Suppression (NMS)   
        keep = non_max_suppression(boxes, scores, iou_threshold=0.5)
        filtered_boxes = boxes[keep].numpy()
        filtered_clss = [clss[i] for i in keep]

        create_voc_xml(image_path, filtered_boxes, folder_path, filtered_clss)

if __name__ == "__main__":
    main()
