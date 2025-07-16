#!/usr/bin/env python3
"""
Football Detection Dataset Augmentation using Albumentations
Augments images and their corresponding YOLO labels with various transformations.
"""

import os
import cv2
import numpy as np
import albumentations as A
from pathlib import Path
import argparse
from tqdm import tqdm


def read_yolo_labels(label_path):
    """
    Read YOLO format labels from a text file.
    
    Args:
        label_path: Path to the label file
        
    Returns:
        List of bounding boxes in YOLO format [class_id, x_center, y_center, width, height]
    """
    if not os.path.exists(label_path):
        return []
    
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    boxes = []
    for line in lines:
        if line.strip():
            values = line.strip().split()
            if len(values) == 5:
                class_id = int(values[0])
                x_center = float(values[1])
                y_center = float(values[2])
                width = float(values[3])
                height = float(values[4])
                boxes.append([class_id, x_center, y_center, width, height])
    
    return boxes


def save_yolo_labels(boxes, output_path):
    """
    Save bounding boxes in YOLO format to a text file.
    
    Args:
        boxes: List of bounding boxes in YOLO format
        output_path: Path to save the label file
    """
    with open(output_path, 'w') as f:
        for box in boxes:
            class_id, x_center, y_center, width, height = box
            f.write(f"{int(class_id)} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")


def create_augmentation_pipeline():
    """
    Create Albumentations augmentation pipeline for object detection in low-light, crowded scenarios,
    including optical distortion and relevant effects for football detection in dark rooms with people.
    """
    return A.Compose([
        # Simulate low light
        A.RandomBrightnessContrast(brightness_limit=(-0.6, 0.1), contrast_limit=0.2, p=0.7),
        # Add random shadows
        A.RandomShadow(p=0.5),
        # Simulate occlusion (people blocking the ball)
        A.CoarseDropout(max_holes=8, max_height=32, max_width=32, min_holes=2, fill_value=0, p=0.4),
        # Color variation
        A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=10, p=0.5),
        # Add noise and blur for realism
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
        A.MotionBlur(blur_limit=5, p=0.2),
        A.GaussianBlur(blur_limit=(3, 7), p=0.2),
        # Optical distortion (lens warping)
        A.OpticalDistortion(distort_limit=0.2, shift_limit=0.05, p=0.2),
        # Horizontal flip for generalization
        A.HorizontalFlip(p=0.5),
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))


def augment_dataset(input_dir, output_dir, augmentations_per_image=3):
    """
    Augment the entire dataset.
    
    Args:
        input_dir: Path to input YOLO dataset directory
        output_dir: Path to output augmented dataset directory
        augmentations_per_image: Number of augmentations per image
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directories
    output_images_dir = output_path / "images"
    output_labels_dir = output_path / "labels"
    output_images_dir.mkdir(parents=True, exist_ok=True)
    output_labels_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all image files
    image_files = list((input_path / "images").glob("*.jpg")) + list((input_path / "images").glob("*.jpeg")) + list((input_path / "images").glob("*.png"))
    
    print(f"Found {len(image_files)} images to augment")
    print(f"Will create {augmentations_per_image} augmentations per image")
    print(f"Total output images: {len(image_files) * (1 + augmentations_per_image)}")
    
    # Create augmentation pipeline
    transform = create_augmentation_pipeline()
    
    # Process each image
    for img_file in tqdm(image_files, desc="Augmenting images"):
        # Read image
        image = cv2.imread(str(img_file))
        if image is None:
            print(f"Warning: Could not read image {img_file}")
            continue
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Read corresponding labels
        label_file = input_path / "labels" / f"{img_file.stem}.txt"
        boxes = read_yolo_labels(label_file)
        
        # Extract class labels for Albumentations
        class_labels = [box[0] for box in boxes]
        bboxes = [box[1:] for box in boxes]  # Remove class_id from boxes
        
        # Save original image and labels
        original_image_path = output_images_dir / img_file.name
        original_label_path = output_labels_dir / f"{img_file.stem}.txt"
        
        cv2.imwrite(str(original_image_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        save_yolo_labels(boxes, original_label_path)
        
        # Create augmentations
        for i in range(augmentations_per_image):
            try:
                # Apply augmentation
                augmented = transform(image=image, bboxes=bboxes, class_labels=class_labels)
                
                # Extract results
                aug_image = augmented['image']
                aug_boxes = augmented['bboxes']
                aug_class_labels = augmented['class_labels']
                
                # Convert back to BGR for saving
                aug_image_bgr = cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)
                
                # Create augmented image name
                aug_image_name = f"{img_file.stem}_aug_{i+1}.jpg"
                aug_label_name = f"{img_file.stem}_aug_{i+1}.txt"
                
                # Save augmented image
                aug_image_path = output_images_dir / aug_image_name
                cv2.imwrite(str(aug_image_path), aug_image_bgr)
                
                # Reconstruct YOLO format boxes and save
                aug_yolo_boxes = []
                for box, class_id in zip(aug_boxes, aug_class_labels):
                    aug_yolo_boxes.append([class_id] + list(box))
                
                aug_label_path = output_labels_dir / aug_label_name
                save_yolo_labels(aug_yolo_boxes, aug_label_path)
                
            except Exception as e:
                print(f"Warning: Failed to augment {img_file.name} (augmentation {i+1}): {e}")
                continue
    
    # Create dataset.yaml for the augmented dataset
    create_dataset_yaml(output_path, len(image_files) * (1 + augmentations_per_image))
    
    print(f"\nAugmentation complete!")
    print(f"Original images: {len(image_files)}")
    print(f"Augmented images: {len(image_files) * augmentations_per_image}")
    print(f"Total images: {len(image_files) * (1 + augmentations_per_image)}")
    print(f"Output directory: {output_path}")


def create_dataset_yaml(output_path, total_images):
    """
    Create dataset.yaml file for the augmented dataset.
    
    Args:
        output_path: Path to the output directory
        total_images: Total number of images in the dataset
    """
    yaml_content = f"""path: {output_path.absolute()}
train: images
val: images

# Classes
nc: 1  # number of classes
names: ['football']  # class names

# Dataset info
total_images: {total_images}
"""
    
    yaml_path = output_path / "dataset.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"Created dataset.yaml at {yaml_path}")


def main():
    parser = argparse.ArgumentParser(description="Augment football detection dataset using Albumentations")
    parser.add_argument("--input", "-i", 
                       default="/home/anass/Desktop/SoSe25/RAML/GitRAML/cvbot-white/data/yolo_dataset",
                       help="Input YOLO dataset directory")
    parser.add_argument("--output", "-o", 
                       default="/home/anass/Desktop/SoSe25/RAML/GitRAML/cvbot-white/data/yolo_dataset_augmented",
                       help="Output augmented dataset directory")
    parser.add_argument("--augmentations", "-a", 
                       type=int, default=3,
                       help="Number of augmentations per image (default: 3)")
    
    args = parser.parse_args()
    
    print("Football Detection Dataset Augmentation")
    print("=" * 50)
    print(f"Input directory: {args.input}")
    print(f"Output directory: {args.output}")
    print(f"Augmentations per image: {args.augmentations}")
    print("=" * 50)
    
    # Check if input directory exists
    if not os.path.exists(args.input):
        print(f"Error: Input directory {args.input} does not exist!")
        return
    
    # Check if images and labels directories exist
    images_dir = os.path.join(args.input, "images")
    labels_dir = os.path.join(args.input, "labels")
    
    if not os.path.exists(images_dir):
        print(f"Error: Images directory {images_dir} does not exist!")
        return
    
    if not os.path.exists(labels_dir):
        print(f"Error: Labels directory {labels_dir} does not exist!")
        return
    
    # Run augmentation
    augment_dataset(args.input, args.output, args.augmentations)


if __name__ == "__main__":
    main() 