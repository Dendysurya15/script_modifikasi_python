 # Import Module
from ast import If
import os
import argparse
from fnmatch import fnmatch

# Read text File


def read_text_file(file_path, output):
	with open(file_path, 'r') as z:
		content = z.readlines()
		out_path = output + '/rekap/rekap.TXT'
		dir_path = output + '/rekap'
  
		if os.path.isdir(dir_path) != True:
			os.makedirs(output + '/rekap')
		unripe = 0
		ripe = 0
		overripe = 0
		empty_bunch = 0
		abnormal = 0
		long_stalk = 0
		dirt = 0

		for x in content:
			class_num = x.split()[0]
			match class_num:
				case '0':
					unripe+=1
				case '1':
					ripe+=1
				case '2':
					overripe+=1
				case '3':
					empty_bunch+=1
				case '4':
					abnormal+=1
				case '5':
					long_stalk+=1
				case '6':
					dirt+=1
		
		file_name = file_path.rsplit("/",1)[-1]
		file_name = file_name.rsplit(".",1)[0]
		write_text_file(out_path, file_name + "," + str(unripe) + "," + str(ripe) + "," + str(overripe) + "," + str(empty_bunch) + "," + str(abnormal) + ","+ str(long_stalk) + ","+ str(dirt))
		print(out_path, file_name + "," + str(unripe) + "," + str(ripe) + "," + str(overripe) + "," + str(empty_bunch) + "," + str(abnormal) + "," +str(long_stalk)+","+ str(dirt))
		z.close()

def write_text_file(output, text):
	with open(output, 'a') as f:
		f.write('\n' + text)
		f.close()

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, default=str(os.getcwd()) + '/rekap', help='input folder path')
print("1")
parser.add_argument('--output', type=str, default=str(os.getcwd()) + '/output', help='output folder path')
print("2")
folder = parser.parse_args().input
print(folder)
output = parser.parse_args().output
print(output)

# Change the directory
os.chdir(folder)
print("5")

for path, subdirs, files in os.walk(folder):
	print("a")
	for name in files:
		if fnmatch(name, "*.txt"):
			print("b")
			# print(os.path.join(path, name))
			read_text_file(os.path.join(path, name), output)
			
""" 
# iterate through all file
for file in os.listdir():
	# Check whether file is in text format or not
	if file.endswith(".txt"):
		file_path = f"{path}\{file}"

		# call read text file function
		read_text_file(file_path)
 """