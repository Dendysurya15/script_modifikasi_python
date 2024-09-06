from ast import If
import os
import argparse
from fnmatch import fnmatch
import shutil
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument('--input_folder', type=str, default=str(os.getcwd()) + '/rekap', help='input folder path')
parser.add_argument('--output_folder', type=str, default=str(os.getcwd()) + '/output', help='output folder path')
parser.add_argument('--input_txt', type=str, help='input txt')
parser.add_argument('--xml', default=True, type=bool, help='is XML?')

input_folder = parser.parse_args().input_folder
output_folder = parser.parse_args().output_folder
input_txt = parser.parse_args().input_txt
xml = parser.parse_args().xml
countNotXML = 0
countFile = 0
countJPEG = 0

print('test')
if os.path.isdir(output_folder) != True:
    os.makedirs(output_folder)

arrIn = []
arrJpg = []

with open(input_txt, 'r') as z:
    for line in z:
        arrIn.append(line.strip())
        arrJpg.append(line.strip()+ ".jpg")
        arrJpg.append(line.strip()+ ".jpeg")
        arrJpg.append(line.strip()+ ".JPG")
        arrJpg.append(line.strip()+ ".JPEG")
arrFile = arrIn

for path, subdirs, files in os.walk(input_folder):
    sama = list(set(files) & set(arrJpg))
    for name in sama:
    # for name in files:
    #     for x in arrIn:
    #         if fnmatch(name, x + ".jpg") or fnmatch(name, x + ".jpeg") or fnmatch(name, x + ".JPG") or fnmatch(name, x + ".JPEG"):
        countJPEG += 1
        ext = name.split(".")[-1]
        x = name[0:((len(ext)+1)*-1)]
        #print(ext)
        #print(x)
        try:
            arrFile.remove(x)
        except:
            print('1')
        # try:
        #         countFile=countFile+1
        #         shutil.copy(path  + x + ".xml", output_folder)
                
        # except:
        #     countNotXML=countNotXML+1
        #copy this file to output folder
        try:
            shutil.copy(path  + name, output_folder + name)
            shutil.copy(path  + x + ".txt", output_folder + x + ".txt")
        except:
            print('file tidak ada bos')
        if xml:
            try:
                countFile=countFile+1
                shutil.copy(path  + x + ".xml", output_folder)
                
            except:
                countNotXML=countNotXML+1
                # print("Tidak ada file xml " + str(name) + " | Count=" + str(countFile) + " | NoXML=" +  str(countNotXML) + " | Sisa=" + str(len(arrFile)))
            
        print("File " + str(name) + " sudah dicopy" + " | Count=" + str(countFile) + " | NoXML=" +  str(countNotXML) + " | Sisa=" + str(len(arrFile))  + " | JPEG=" + str(countJPEG) )

with open(path +"/sisa.txt", "a") as f:
    for o in arrFile:
        f.write(o + "\n")


                
                    

