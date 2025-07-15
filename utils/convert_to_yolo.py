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
    
    # Copy images and create label files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

    # counter to track how many images we have processed successfully
    processed_count = 0
    
    # here we loop through each image in the annotations and copy the image to the YOLO images directory
    for image_id, labels in annotations.items():
        # Find the image file
        image_found = False # flag to check if the image is found
        for file_extension in image_extensions: # loop through the image extensions we created and init before
            image_path = os.path.join(images_dir, f"{image_id}{file_extension}") # image id + file extension. (e. g football1 + .jpg = football1.jpg)
            if os.path.exists(image_path):
                # Copy image to YOLO images directory
                shutil.copy2(image_path, os.path.join(yolo_images_dir, f"{image_id}{file_extension}"))
                
                # Create label file
                label_path = os.path.join(yolo_labels_dir, f"{image_id}.txt")
                with open(label_path, 'w') as f:
                    for label in labels:
                        f.write(label + '\n')
                
                image_found = True
                processed_count += 1
                break
        
        if not image_found:
            print(f"Warning: Image {image_id} not found in {images_dir}")
    
    # Ensure every image has a label file (empty if no annotation)
    for filename in os.listdir(images_dir):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in image_extensions:
            continue
        label_path = os.path.join(yolo_labels_dir, f"{name}.txt")
        if not os.path.exists(label_path):
            open(label_path, 'w').close()  # Create empty file

    #print(f"Processed {processed_count} images with annotations")
    #print(f"YOLO DAtaset created in: {output_dir}")
    
    # Create dataset.yaml file
    # YOLO dataset configuration
    dataset_yaml = f"""path: {os.path.abspath(output_dir)}
train: images
val: images

# Classes
nc: 1  # number of classes
names: ['football']  # class names
"""
    
    with open(os.path.join(output_dir, "dataset.yaml"), 'w') as f:
        f.write(dataset_yaml)
    
    print(f"Dataset configuration saved to: {os.path.join(output_dir, 'dataset.yaml')}")

if __name__ == "__main__":
    # Paths
    annotation_file = "./data/annotations/openimage_annotations.csv"
    images_dir = "./data/images"
    output_dir = "./data/yolo_dataset"

    
    convert_openimage_to_yolo(annotation_file, images_dir, output_dir) 
