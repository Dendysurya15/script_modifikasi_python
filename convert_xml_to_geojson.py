import os
import xml.etree.ElementTree as ET
import json
import argparse

def parse_xml_file(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract bounding box coordinates
    features = []
    for obj in root.findall('object'):
        bndbox = obj.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)

        # Create a GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [xmin, ymin],
                    [xmin, ymax],
                    [xmax, ymax],
                    [xmax, ymin],
                    [xmin, ymin]
                ]]
            },
            "properties": {}
        }
        features.append(feature)

    return features

def create_geojson(features, geojson_file):
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(geojson_file, 'w') as f:
        json.dump(geojson, f, indent=2)

def process_folder(source_folder):
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.xml'):
            xml_file = os.path.join(source_folder, file_name)
            geojson_file = os.path.join(source_folder, os.path.splitext(file_name)[0] + '.geojson')

            features = parse_xml_file(xml_file)
            create_geojson(features, geojson_file)

def main():
    parser = argparse.ArgumentParser(description="Convert XML bounding box annotations to GeoJSON format.")
    parser.add_argument('--source', type=str, required=True, help="Source folder containing XML files.")
    args = parser.parse_args()

    source_folder = args.source

    if not os.path.isdir(source_folder):
        print(f"The source folder {source_folder} does not exist.")
        return

    process_folder(source_folder)
    print("GeoJSON files created successfully for all XML files in the folder.")

if __name__ == "__main__":
    main()
