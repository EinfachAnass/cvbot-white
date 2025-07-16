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
            x_min = float(row['XMin'])
            x_max = float(row['XMax'])
            y_min = float(row['YMin'])
            y_max = float(row['YMax'])
            
            # YOLO format: <class> <x_center> <y_center> <width> <height> 
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            width = x_max - x_min
            height = y_max - y_min
            
            class_id = class_mapping.get(row['LabelName'], 0)
            
            annotations[image_id].append(f"{class_id} {x_center} {y_center} {width} {height}")
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    processed_count = 0
    
    # First, copy all images from images_dir to yolo_images_dir
    for filename in os.listdir(images_dir):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in image_extensions:
            continue
        src_path = os.path.join(images_dir, filename)
        dst_path = os.path.join(yolo_images_dir, filename)
        if not os.path.exists(dst_path):
            shutil.copy2(src_path, dst_path)
    
    # Now, create label files for all images
    for filename in os.listdir(images_dir):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in image_extensions:
            continue
        label_path = os.path.join(yolo_labels_dir, f"{name}.txt")
        if name in annotations:
            # Write YOLO labels
            with open(label_path, 'w') as f:
                for label in annotations[name]:
                    f.write(label + '\n')
            processed_count += 1
        else:
            # Create empty label file
            open(label_path, 'w').close()
    
    # Create dataset.yaml file
    dataset_yaml = f"""path: {os.path.abspath(output_dir)}\ntrain: images\nval: images\n\n# Classes\nnc: 1  # number of classes\nnames: ['football']  # class names\n"""
    
    with open(os.path.join(output_dir, "dataset.yaml"), 'w') as f:
        f.write(dataset_yaml)
    
    print(f"Dataset configuration saved to: {os.path.join(output_dir, 'dataset.yaml')}")

if __name__ == "__main__":
    # Paths
    annotation_file = "./data/annotations/openimage_annotations.csv"
    images_dir = "./data/images"
    output_dir = "./data/yolo_dataset"

    convert_openimage_to_yolo(annotation_file, images_dir, output_dir) 