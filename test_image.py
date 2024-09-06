from ultralytics import YOLO

# Load a pretrained YOLOv8n model
model = YOLO("/home/grading/yolov8/2024-05-27-14-21_yolov5su_1280_48_foto_mei/train/weights/best.pt")

# Run inference on 'bus.jpg' with arguments
model.predict("/home/grading/MRE-FOTO-UDARA-JPG/mre-1-blok.jpg", save=True, imgsz=9200, conf=0.01,iou=1,max_det=12000, show_labels=False, show_conf=False, line_width=4)
# model.predict("/home/grading/MRE-FOTO-UDARA-JPG/mre-1-blok.jpg", save=True, imgsz=10758, conf=0.01,iou=0.3,max_det=12000, show_labels=False, show_conf=False, line_width=4)