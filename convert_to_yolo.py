import csv
import os
import shutil


def convert_openimage_to_yolo(annotation_file, images_dir, output_dir):
    """
    Convert OpenImageV7 annotations to YOLO format
    """
    # Create output directories using the strict folder structure required by YOLO /images and /labels
    yolo_images_dir = os.path.join(output_dir, "images")
    yolo_labels_dir = os.path.join(output_dir, "labels")
    # if we run the script again and again it wont crash if the folders already exist (exist_ok=True)
    os.makedirs(yolo_images_dir, exist_ok=True) 
    os.makedirs(yolo_labels_dir, exist_ok=True)
    
    # Class mapping by mapping the OpenImageV7 Football ID which is 201 to the first YOLO class which is 0 
    # since football is our only class
    class_mapping = {"201": 0}  
    
    # Read annotations
    annotations = {}
    with open(annotation_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_id = row['ImageID']
            if image_id not in annotations: 
                annotations[image_id] = []
            
            # Convert normalized coordinates to YOLO format 
            x_min = float(row['XMin']) # get the left edge coordinate and convert it to float
            x_max = float(row['XMax']) # get the right edge 
            y_min = float(row['YMin']) # get the top edge 
            y_max = float(row['YMax']) # get the bottom 
            
            # YOLO format: <class> <x_center> <y_center> <width> <height> 
            # OpenImageV7 uses corner coordinates (top left and bottom right corners) and YOLO uses center 
            # coordinates (center point + width and height)
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            width = x_max - x_min
            height = y_max - y_min
            
            # get the class id from the class mapping. Default to 0 if the class is not found
            class_id = class_mapping.get(row['LabelName'], 0)
            
            # create YOLO format string and add it to the annotations list
            annotations[image_id].append(f"{class_id} {x_center} {y_center} {width} {height}")
    
