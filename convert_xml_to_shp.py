import os
import xml.etree.ElementTree as ET
import shapefile
import argparse

def parse_xml_file(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract bounding box coordinates
    bndboxes = []
    for obj in root.findall('object'):
        bndbox = obj.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        bndboxes.append((xmin, ymin, xmax, ymax))

    return bndboxes

def create_shapefile(bndboxes, shp_file):
    # Create a shapefile writer object
    with shapefile.Writer(shp_file) as shp:
        shp.autoBalance = 1
        shp.field('ID', 'N')

        # Add the bounding box coordinates as polygons
        for idx, (xmin, ymin, xmax, ymax) in enumerate(bndboxes):
            # Define the polygon points
            points = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)]
            shp.poly([points])
            shp.record(idx)

def process_folder(source_folder):
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.xml'):
            xml_file = os.path.join(source_folder, file_name)
            shp_file = os.path.join(source_folder, os.path.splitext(file_name)[0] + '.shp')

            bndboxes = parse_xml_file(xml_file)
            create_shapefile(bndboxes, shp_file)

def main():
    parser = argparse.ArgumentParser(description="Convert XML bounding box annotations to shapefile format.")
    parser.add_argument('--source', type=str, required=True, help="Source folder containing XML files.")
    args = parser.parse_args()

    source_folder = args.source

    if not os.path.isdir(source_folder):
        print(f"The source folder {source_folder} does not exist.")
        return

    process_folder(source_folder)
    print("Shapefiles created successfully for all XML files in the folder.")

if __name__ == "__main__":
    main()
