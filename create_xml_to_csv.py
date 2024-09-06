import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import argparse

def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df

def main(input_folder):
    for folder in ['train', 'validation', 'test']:
        image_path = os.path.join(input_folder, ('images/' + folder))
        xml_df = xml_to_csv(image_path)
        xml_df.to_csv(os.path.join(input_folder, ('images/' + folder + '_labels.csv')), index=None)
        print(f'Successfully converted xml to csv for {folder}.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-folder', type=str, required=True, help='Root directory of the dataset')
    args = parser.parse_args()
    main(args.input_folder)
