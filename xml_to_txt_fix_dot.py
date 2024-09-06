# COMMAND : py xml_to_txt.py -i car\xmls -o car\txts
# Here you need to change the dictionary as per your classes
import os
import glob
import argparse
from xml.dom import minidom

def convert_coordinates(size, box):
    dw = 1.0/size[0]
    dh = 1.0/size[1]
    x = (box[0]+box[1])/2.0
    y = (box[2]+box[3])/2.0
    w = box[1]-box[0]
    h = box[3]-box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,abs(w),abs(h))

def xml_to_txt( lut ,input ,output):

    # Start writing  
    for xml in glob.glob( os.path.join(input , "*.xml") ):
        try:
            xmldoc = minidom.parse(xml)  
            fname_out = xml.split("\\")[-1]
            
            if len(fname_out.split(".")[-1]) == 3:
                fname_out = (os.path.join(output, fname_out[0:-4]+ '.txt'))
            elif len(fname_out.split(".")[-1]) == 4:
                fname_out = (os.path.join(output, fname_out[0:-5]+ '.txt'))

            with open(fname_out, "w") as f:
                # Get image properties
                itemlist = xmldoc.getElementsByTagName('object')
                size = xmldoc.getElementsByTagName('size')[0]
                width = int((size.getElementsByTagName('width')[0]).firstChild.data)
                height = int((size.getElementsByTagName('height')[0]).firstChild.data)
                
                for item in itemlist:
                    # get class label
                    classid =  (item.getElementsByTagName('name')[0]).firstChild.data.lower()
                    if classid in lut:
                        label_str = str(lut[classid])
                    else:
                        # label_str = "-1"
                        # print ("warning: label '%s' not in look-up table" % classid)
                        # print(f"Warning: label '{classid}' not in look-up table in file {xml}")
                        print(f"Warning: label '{classid}' not in look-up table in file {os.path.basename(xml)}")
                        continue
                        
                    # get bbox coordinates
                    xmin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmin')[0]).firstChild.data
                    ymin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymin')[0]).firstChild.data
                    xmax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmax')[0]).firstChild.data
                    ymax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymax')[0]).firstChild.data
                    b = (float(xmin), float(xmax), float(ymin), float(ymax))
                    bb = convert_coordinates((width,height), b)
                    # Write out the file
                    f.write(label_str + " " + " ".join([("%.6f" % a) for a in bb]) + '\n')
        except Exception as e:
            print(f"Error parsing XML file {xml}: {e}")
            continue
        # define output filename    

        
     

        # print ("wrote %s" % fname_out)    

if __name__ == '__main__' :
    # Argument Parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True, help="Xmls path")
    ap.add_argument("-o", "--output", required=True, help="output directory ")
    args = vars(ap.parse_args())   

    # Create output path if not already exists
    if not os.path.exists(args["output"]):
       os.makedirs(args["output"])

    #  Define your classes , you can add more 
    lut={}
    # lut["unripe"] = 0
    # lut["ripe"] = 1
    # lut["overripe"] = 2
    # lut["empty_bunch"] = 3
    # lut["abnormal"] = 4
    # lut["long_stalk"] = 5
    # lut["dirt"] = 6

    # lut["adoretus_dewasa"] =  0
    # lut["amathusia_dewasa"] =  1
    # lut["amathusia_larva"] =  2
    # lut["amathusia_pupa"] =  3
    # lut["ambadra_dewasa"] =  4
    # lut["aphis_sp_dewasa"] =  5
    # lut["aphis_sp_telur"] =  6
    # lut["birthamula_dewasa"] =  7
    # lut["birthamula_larva"] =  8
    # lut["birthosea_bisura_larva"] =  9
    # lut["calliteara_dewasa"] =  10
    # lut["calliteara_telur"] =  11
    # lut["dasychira_mendosa_dewasa"] =  12
    # lut["dasychira_mendosa_larva"] =  13
    # lut["dasychira_mendosa_pupa"] =  14
    # lut["dasychira_mendosa_telur"] =  15
    # lut["helopeltis_dewasa"] =  16
    # lut["helopeltis_nymph"] =  17
    # lut["locusta_migratoria_dewasa"] =  18
    # lut["locusta_migratoria_nymph"] =  19
    # lut["oryctes_rhinoceros_dewasa"] =  20
    # lut["parasa_lepida_larva"] =  21
    # lut["rhabdoscelus_dewasa"] =  22
    # lut["rhynchophorus_dewasa"] =  23
    # lut["spodoptera_litura_dewasa"] =  24
    # lut["valanga_nigricornis_dewasa"] =  25

    # lut["normal"] = 0
    # lut["abnormal"] = 1

    lut["abnormal"] = 0
    lut["normal"] = 1

    # lut["janjang"] = 0

    # lut["mouse"] = 0

    # Write out to txts
    xml_to_txt( lut , args["input"], args["output"])