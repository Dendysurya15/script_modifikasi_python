

from email.mime import image
import os
from xml.etree.ElementTree import Element, ElementTree
from PIL import Image

def convert_txt_to_xml(txt_path, xml_path, class_mapping):
    txt_files = [f for f in os.listdir(txt_path) if f.endswith('.txt')]
    for i, txt_file in enumerate(txt_files):
        txt_file_path = os.path.join(txt_path, txt_file)
        xml_file_name = os.path.splitext(txt_file)[0] + '.xml'
        xml_file_path = os.path.join(xml_path, xml_file_name)

        # Specify the path to the file
        file_path_b4 = txt_path + txt_file
        file_path = file_path_b4[:-4]

        # Check if the path is a regular file
        if os.path.isfile(file_path+'.jpg'):
            image = Image.open(file_path+'.jpg')
        elif os.path.isfile(file_path+'.jpeg'):
            image = Image.open(file_path+'.jpeg')
        elif os.path.isfile(file_path+'.JPG'):
            image = Image.open(file_path+'.JPG')
        elif os.path.isfile(file_path+'.JPEG'):
            image = Image.open(file_path+'.JPEG')
        elif os.path.isfile(file_path+'.png'):
            image = Image.open(file_path+'.png')
        elif os.path.isfile(file_path+'.PNG'):
            image = Image.open(file_path+'.PNG')
        else:
            print(f"{file_path} is not a regular file. ({i}/{len(txt_files)})")
            continue

        # Get the width and height
        try:
            width, height = image.size
            image_mode = image.mode

            widthX = width
            heightX = height

            # Extract the depth from the mode
            image_depth = len(image_mode)

            with open(txt_file_path, 'r') as txt_file:
                lines = txt_file.readlines()

            root = Element('annotation')
            folder = Element('folder')
            folder.text = os.path.dirname(txt_file_path)
            root.append(folder)
    
            filename = Element('filename')

            extension_image = os.path.splitext(image.filename)[1]
            filename.text = os.path.splitext(os.path.basename(txt_file_path))[0]  + extension_image
            root.append(filename)

            size = Element('size')
            width = Element('width')
            width.text = str(widthX)  # Default width value
            height = Element('height')
            height.text = str(heightX)  # Default height value
            depth = Element('depth')
            depth.text = str(image_depth)  # Assuming 3 channels for RGB images
            size.append(width)
            size.append(height)
            size.append(depth)
            root.append(size)

            for line in lines:
                line = line.strip().split()
                if len(line) >= 5:
                    obj = Element('object')
                    name = Element('name')
                    pose = Element('pose')
                    truncated = Element('truncated')
                    difficult = Element('difficult')
                    bndbox = Element('bndbox')
                    xmin = Element('xmin')
                    ymin = Element('ymin')
                    xmax = Element('xmax')
                    ymax = Element('ymax')
                    obj.append(name)
                    obj.append(pose)
                    obj.append(truncated)
                    obj.append(difficult)
                    obj.append(bndbox)
                    bndbox.append(xmin)
                    bndbox.append(ymin)
                    bndbox.append(xmax)
                    bndbox.append(ymax)
                    root.append(obj)

                    class_id = int(line[0])
                    if class_id in class_mapping:
                        class_name = class_mapping[class_id]
                    else:
                        class_name = 'unknown'
                    name.text = class_name
                    pose.text = 'Unspecified'
                    truncated.text = '0'
                    difficult.text = '0'

                    x_center = line[1]
                    y_center = line[2]
                    widthL = line[3]
                    heightL = line[4]

                    xmin.text = str(int(float(x_center) * widthX - (float(widthL) * widthX) / 2))
                    ymin.text = str(int(float(y_center) * heightX - (float(heightL) * heightX) / 2))
                    xmax.text = str(int(float(x_center) * widthX + (float(widthL) * widthX) / 2))
                    ymax.text = str(int(float(y_center) * heightX + (float(heightL) * heightX) / 2))

                    # # if len(line) >= 7:
                    # xmin.text = line[1]
                    # ymin.text = line[2]1088
                    # xmax.text = str(float(line[1]) + float(line[3]))
                    # ymax.text = str(float(line[2]) + float(line[4]))
                # else:
                    #     xmin.text = '0'  # Default xmin value
                    #     ymin.text = '0'  # Default ymin value
                    #     xmax.text = '0'  # Default xmax value
                    #     ymax.text = '0'  # Default ymax value
                else:
                    # Handle cases where bounding box coordinates are not provided
                    continue

            xml_tree = ElementTree(root)
            xml_tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
        except:
            print("ga ada JPEGnya")

txt_path = '/home/grading/Project_Hama_AI/12_class/project-4-at-2024-05-25-07-31-51ee02ae/12_class_more_100_labels/all/val/'  # Path to the txt annotation file directory
xml_path = '/home/grading/Project_Hama_AI/12_class/project-4-at-2024-05-25-07-31-51ee02ae/12_class_more_100_labels/all/val/'  # Path to save the xml annotation file directory
# class_mapping = {0: 'normal', 1: 'abnormal'}  # Replace
# class_mapping = {0: 'janjang'}

class_mapping = {
    0: 'adoretus_dewasa',
    1: 'amathusia_dewasa',
    2: 'amathusia_larva',
    3: 'amathusia_pupa',
    4: 'ambadra_dewasa',
    5: 'aphis_sp_dewasa',
    6: 'aphis_sp_telur',
    7: 'birthamula_dewasa',
    8: 'birthamula_larva',
    9: 'birthosea_bisura_larva',
    10: 'calliteara_dewasa',
    11: 'calliteara_telur',
    12: 'dasychira_mendosa_dewasa',
    13: 'dasychira_mendosa_larva',
    14: 'dasychira_mendosa_pupa',
    15: 'dasychira_mendosa_telur',
    16: 'helopeltis_dewasa',
    17: 'helopeltis_nymph',
    18: 'locusta_migratoria_dewasa',
    19: 'locusta_migratoria_nymph',
    20: 'oryctes_rhinoceros_dewasa',
    21: 'parasa_lepida_larva',
    22: 'rhabdoscelus_dewasa',
    23: 'rhynchophorus_dewasa',
    24: 'spodoptera_litura_dewasa',
    25: 'valanga_nigricornis_dewasa'
}


convert_txt_to_xml(txt_path, xml_path, class_mapping)
