from collections import defaultdict
from unittest import result
import qrcode
import cv2
import numpy as np
import argparse
from ultralytics import YOLO
import datetime
import os
import threading
from datetime import datetime
from datetime import date
import pytz
from pathlib import Path
from PIL import Image
from ultralytics.utils.plotting import Annotator
import pymssql
from reportlab.pdfgen import canvas
from reportlab.lib import colors as colorPdf
from collections import Counter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Image as ImgRl
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.platypus import Spacer
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import re
import subprocess
import json
import sys
from time import time, sleep
import random
import string
from queue import Queue
import atexit
import xml.etree.ElementTree as ET
from xml.dom import minidom



parser = argparse.ArgumentParser()
parser.add_argument('--yolo_model', type=str, default='/home/grading/yolov8/weight/training_24_november_total/weights/best.pt', help='model.pt path')
parser.add_argument('--source', type=str, default='./video/Sampel Scm.mp4', help='source')  # file/folder, 0 for webcam
parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=1280, help='inference size h,w')
parser.add_argument('--conf_thres', type=float, default=0.05, help='object confidence threshold')
parser.add_argument('--iou_thres', type=float, default=0.5, help='IOU threshold for NMS')
parser.add_argument('--tracker', type=str, default='botsort.yaml', help='bytetrack.yaml or botsort.yaml')
parser.add_argument('--roi', type=float, default=0.43, help='line height')
parser.add_argument('--show', type=bool, default=True, help='line height')
parser.add_argument('--save_vid', type=bool, default=False)
parser.add_argument("--debug", type=bool, default=False, help="Enable debug mode to store everything printed result into txt file")
parser.add_argument("--tiket", type=str, default='default', help="Enable debug mode to store everything printed result into txt file")
opt = parser.parse_args()
yolo_model_str = opt.yolo_model
source = opt.source
imgsz = opt.imgsz
conf_thres = opt.conf_thres
iou_thres = opt.iou_thres
tracker = opt.tracker
roi = opt.roi
show = opt.show
save_vid = opt.save_vid
debug = opt.debug
no_tiket = opt.tiket
TotalJjg = 0
timer = 25
stream = None
ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'
connection = None

source_filename_without_extension = Path(opt.source)

# Extract date folder and file name without extension
date_folder = source_filename_without_extension.parent.name
file_name_without_extension = source_filename_without_extension.stem


def contains_video_keywords(file_path):
    # Define a list of keywords that are commonly found in video file names
    video_keywords = ['avi', 'mp4', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v']

    # Convert the file path to lowercase for case-insensitive matching
    file_path_lower = file_path.lower()

    # Check if any of the video keywords are present in the file path
    for keyword in video_keywords:
        if keyword in file_path_lower:
            return True

    return False
# Use regular expression to find the IP address in the source string
ip_match = re.search(ip_pattern, source)

if ip_match:
    extracted_ip = ip_match.group(1)
    stream = f'rtsp://admin:gr4d!ngs@{extracted_ip}/video'
elif contains_video_keywords(source):
    stream = source
else:
    stream = str(Path(os.getcwd() + '/video/Sampel Scm.mp4'))
    

# Load the YOLOv8 model
model = YOLO(yolo_model_str)

# Open the video filfe
video_path = stream
cap = cv2.VideoCapture(video_path)

# Store the track history
track_history = defaultdict(lambda: [])

# Initialize variables for counting
countOnFrame = 0
kastrasi = 0
kas_reset = 0
skor_tertinggi = 0
jum_tertinggi = 0
skor_terendah = 1000
object_ids_passed = []
object_ids_not_passed = []
baseScore = [0,3,2,0,2,1]
names = list(model.names.values())
class_count = [0] * len(names)
class_count_reset = [0] * len(names)


hexs = ['FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7']
bgr_colors = []

for hex_color in hexs:
    # Convert hex to BGR
    blue = int(hex_color[4:6], 16)
    green = int(hex_color[2:4], 16)
    red = int(hex_color[0:2], 16)
    
    bgr_colors.append((blue, green, red))  # Appending as (Blue, Green, Red)\

max_area = 280000
font = 2
fontRipeness = 1
log_inference = Path(os.getcwd() + '/log_inference_sampling')
tzInfo = pytz.timezone('Asia/Bangkok')
current_date = datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')
log_inference.mkdir(parents=True, exist_ok=True)  # make dir
save_dir_txt = Path(os.getcwd() + '/hasil/temp.TXT')
if not save_dir_txt.exists():
    log_folder = os.path.dirname(save_dir_txt)
    os.makedirs(log_folder, exist_ok=True)
    save_dir_txt.touch()
grading_total_dir = Path(os.getcwd() + '/hasil/grading_total_log.TXT')
if not grading_total_dir.exists():
    log_folder = os.path.dirname(grading_total_dir)
    os.makedirs(log_folder, exist_ok=True)
    grading_total_dir.touch()


date_start = datetime.now(tz=tzInfo).strftime("%Y-%m-%d %H:%M:%S")
date_end = None
date_start_no_space = str(date_start).split(' ')
bt = False
timer_start = datetime.now(tz=tzInfo)

def mouse_callback(event, x, y, flags, param):
    
    global bt  # Declare that you want to modify the global variable bt
    
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click event
        #print(f"Mouse clicked at ({x}, {y})")
        if x > 1720 and y < 200:
            bt = True

def generate_random_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))
random_code = None
def save_img_async(img, name_file):
    dt = date.today()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgP = Image.frombytes("RGB", (int(img.shape[1]), int(img.shape[0])), img)
    myHeight, myWidth = imgP.size
    imgP = imgP.resize((myHeight, myWidth))

    directory_path = './auto_labelling_video/'

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")

    img_path = directory_path + f"{name_file}.JPG"

    imgP.save(img_path, optimize=True, quality=80)
    print(f"Image saved: {img_path}")

def close():
    print('program has been closed')
   
    
last_id = 0
track_idsArr = []
prefix = ''

window = "Yolov8 "+str(imgsz) + " CONF-" + str(conf_thres) + " IOU-" +  str(iou_thres) + " SRC-" + source + " MODEL-" + yolo_model_str
cv2.namedWindow(window)
cv2.setMouseCallback(window, mouse_callback)
cv2.setWindowProperty(window,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)



def capture_screenshots():
    global random_code
    while not screenshot_thread_stop_flag.is_set():
        screenshot_event.wait()
        screenshot_event.clear()
        if not screenshot_thread_stop_flag.is_set():  # Check if thread should continue
            # random_code = generate_random_code()
            index = 100
            dt = date.today()
            _, frame = cap.read()

            # print(cobax)
            # print(cobay)
            save_img_async(frame, str(dt) + '_' + random_code)
       

screenshot_event = threading.Event()
screenshot_thread_stop_flag = threading.Event()
screenshot_thread = threading.Thread(target=capture_screenshots)
screenshot_thread.start()   

def stop_screenshot_thread():
    screenshot_event.set()  # Set the event to signal screenshot capture
    screenshot_thread_stop_flag.set()
    screenshot_thread.join(timeout=1)

class_mapping = {
    0: "unripe",
    1: "ripe",
    2: "overripe",
    3: "empty_bunch",
    4: "abnormal"
}
output_directory = os.path.join(os.getcwd(), 'auto_labelling_video')


if not os.path.exists(output_directory):
    os.makedirs(output_directory)
    print(f"Directory '{output_directory}' created successfully.")

try:
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        if success:
            start_time = time()

            results = model.track(frame, persist=True, conf=conf_thres, iou=iou_thres, imgsz=imgsz, tracker=tracker, verbose=False,stream_buffer=True)
            
            end_time = time()

            fps = 1 / (end_time - start_time)

            boxes = results[0].boxes.xywh.cpu()

            
                
            try:
                track_ids = results[0].boxes.id.int().cpu().tolist()
            except Exception as e:
                track_ids = []
            clss = results[0].boxes.cls.cpu().tolist()

            annotated_frame = results[0].plot(conf=False)
        
            middle_y = (frame.shape[0] * (1-float(roi)))

            prctg_middle_y_bawah = middle_y * 30 / 100

            prctg_middle_y_atas = middle_y * 60 / 100

            middle_y_bawah = middle_y + prctg_middle_y_bawah

            middle_y_atas = middle_y - prctg_middle_y_atas

            
            cv2.line(annotated_frame, (0, int(middle_y)), (annotated_frame.shape[1], int(middle_y)), (0, 255, 0), 2)  
            
            
            skorTotal = 0
            countOnFrame = 0
            nilai = 0

            track_idsArr.append(track_ids)
            
            arrY = []
            for box, track_id, cl in zip(boxes, track_ids, clss):
                

                
                x, y, w, h = box
                xmin, ymin, xmax, ymax = int(x), int(y), int(x + w), int(y + h)
           
                wideArea = int(w) * int(h)
                entry = {track_id: wideArea}
        
                arrY.append(wideArea)        

                track = track_history[track_id]
                
                track.append((float(x), float(y))) 


                
            
                if middle_y > y and track_id not in object_ids_not_passed:
                
                    object_ids_not_passed.append(track_id)
                
                if y > middle_y  and track_id not in object_ids_passed and track_id in object_ids_not_passed:
                    # buah_paling_bawah = int(arrY[0])
                    # buah_paling_atas = int(arrY[-1])
                    
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

                    random_code = generate_random_code()
                    dt = date.today()
                    screenshot_event.set()
                    # Save XML
                    xml_filename = os.path.join(output_directory, f"{dt}_{random_code}.xml")
                    xml_string = minidom.parseString(ET.tostring(annotation)).toprettyxml(indent="    ")
                    with open(xml_filename, "w") as f:
                        f.write(xml_string)
                    
                    
                 
                    
                    # print(buah_paling_atas)



                    # if buah_paling_atas > max_area and buah_paling_bawah > max_area:
                        
                        # print('nais')
                        


                    # else:
                    #     screenshot_queue.put(False)
                        # for _ in range(3):
                        #     save_img_async(annotated_frame, str(dt) + '_' + str(track_ids))
                        #     sleep(0.1)  # 100ms delay
                    # save_img_async_wrapper(annotated_frame, str(dt) + '_' + str(track_id))
                    # save_img_async_wrapper(annotated_frame, str(dt) + '_' + str(track_id))
                    # save_img_async_wrapper(annotated_frame, str(dt) + '_' + str(track_id))
                    # save_img_async_wrapper(annotated_frame)
                    # delay_count += 1
                    # if delay_count >= delay_threshold:
                    #     delay_thread = threading.Thread(target=introduce_delay)
                    #     delay_thread.start()
                
                    tid = False
                    for tis in track_idsArr:
                        if int(track_id) in tis:
                            tid = True
                            break
                
                    if tid:
                        try:
                            object_ids_not_passed.remove(track_id)
                        except Exception as e:
                            print("error cannot remove track_id:" + str(e))
                        


            width, height = 100, 100
            background_color = (255, 255, 255)  # White in BGR format

            # Define the center and radius of the circular stop sign
            center = (width // 2, height // 2)
            radius = width // 2 - 5  # Leave a small border

            cv2.circle(annotated_frame, (1820,100), radius, (0, 0, 255), -1)  # Red in BGR format

            # Create the white border
            cv2.circle(annotated_frame, (1820,100), radius, (255, 255, 255), 5)
            cv2.putText(annotated_frame, window, (10, 1070), cv2.FONT_HERSHEY_PLAIN, 1, (150, 0, 0), 4)
            cv2.putText(annotated_frame, window, (10, 1070), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

            # Display the annotated frame
            cv2.imshow(window, annotated_frame)

        
            if cv2.waitKey(1) & 0xFF == ord("q") or bt:
                close()
                stop_screenshot_thread()
                break
                

        else:
            close()
            break
        
except KeyboardInterrupt:
    print("KeyboardInterrupt: Stopping threads...")
    stop_screenshot_thread()
    

stop_screenshot_thread()
cap.release()
cv2.destroyAllWindows()

   
    
  


