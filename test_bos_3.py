import cv2
import os
import argparse
from ultralytics import YOLO
from lxml import etree

def create_xml(image_path, results, class_mapping, output_folder):
    # Read the image
    image = cv2.imread(image_path)

    # Create the XML root element
    annotation = etree.Element("annotation")

    # Add image details to the XML
    folder = etree.SubElement(annotation, "folder")
    folder.text = os.path.basename(os.path.dirname(image_path))

    filename = etree.SubElement(annotation, "filename")
    filename.text = os.path.basename(image_path)

    size = etree.SubElement(annotation, "size")
    width = etree.SubElement(size, "width")
    width.text = str(image.shape[1])

    height = etree.SubElement(size, "height")
    height.text = str(image.shape[0])

    depth = etree.SubElement(size, "depth")
    depth.text = str(image.shape[2])

    # Add detected objects to the XML
    for result in results:
        for box in result.boxes:
            obj = etree.SubElement(annotation, "object")
            
            name = etree.SubElement(obj, "name")
            name.text = class_mapping[int(box.cls)]
            
            bndbox = etree.SubElement(obj, "bndbox")
            xmin = etree.SubElement(bndbox, "xmin")
            xmin.text = str(int(box.xyxy[0]))
            
            ymin = etree.SubElement(bndbox, "ymin")
            ymin.text = str(int(box.xyxy[1]))
            
            xmax = etree.SubElement(bndbox, "xmax")
            xmax.text = str(int(box.xyxy[2]))
            
            ymax = etree.SubElement(bndbox, "ymax")
            ymax.text = str(int(box.xyxy[3]))

    # Convert the XML to a string
    xml_str = etree.tostring(annotation, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    # Save the XML to a file
    xml_output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(image_path))[0] + ".xml")
    with open(xml_output_path, "wb") as xml_file:
        xml_file.write(xml_str)

    print(f"XML output saved to {xml_output_path}")

def main(input_folder, output_folder):
    # Load the YOLOv8 model
    model = YOLO("/home/grading/yolov8/2024-05-27-14-21_yolov5su_1280_48_foto_mei/train/weights/best.pt")

    # Class mapping
    class_mapping = {
        0: "normal",
        1: "abnormal"
    }

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each image in the input folder
    for image_file in os.listdir(input_folder):
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, image_file)
            # Perform object detection
            results = model(image_path)
            # Create XML for the detected objects
            create_xml(image_path, results, class_mapping, output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process images in a folder and create XML output for detected objects.")
    parser.add_argument('--input_folder', type=str, required=True, help="Path to the input folder containing images.")
    parser.add_argument('--output_folder', type=str, required=True, help="Path to the output folder for XML files.")

    args = parser.parse_args()
    main(args.input_folder, args.output_folder)
