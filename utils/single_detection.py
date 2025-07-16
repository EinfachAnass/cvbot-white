#!/usr/bin/env python3
"""
Single Image Detection Script
Uses trained YOLO model to detect ball in a single image
"""

import cv2
import numpy as np
from ultralytics import YOLO
import os
import sys

def detect_ball_in_image(model_path, image_path, conf_threshold=0.5):
    """
    Detect ball in a single image using trained YOLO model
    
    Args:
        model_path (str): Path to the trained YOLO model (.pt file)
        image_path (str): Path to the input image
        conf_threshold (float): Confidence threshold for detections
    
    Returns:
        tuple: (image with boxes drawn, detection results)
    """
    
    # Load the model
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return None, None
    
    # Load and process the image
    print(f"Processing image: {image_path}")
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return None, None
    
    print(f"Image shape: {image.shape}")
    
    # Perform detection
    results = model(image, conf=conf_threshold)
    
    # Process results using YOLO's built-in plotting
    detections = []
    
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Get confidence
                confidence = float(box.conf[0].cpu().numpy())
                
                # Get class (should be 0 for ball)
                class_id = int(box.cls[0].cpu().numpy())
                
                # Calculate center point
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Store detection info
                detection_info = {
                    'bbox': (x1, y1, x2, y2),
                    'center': (center_x, center_y),
                    'confidence': confidence,
                    'class_id': class_id
                }
                detections.append(detection_info)
                
                print(f"Detection: Ball at center ({center_x}, {center_y}) with confidence {confidence:.3f}")
    
    if not detections:
        print("No ball detected in the image")
    
    # Use YOLO's built-in plotting for proper visualization
    result_image = results[0].plot()  # This gives you the proper YOLO-style boxes
    
    return result_image, detections

def main():
    # Configuration
    model_path = "/home/anass/Desktop/SoSe25/RAML/GitRAML/cvbot-white/models/football_detector/weights/best.pt"  # Adjust path to your model
    image_path = "/home/anass/Downloads/Test_img.jpeg"
    conf_threshold = 0.3  # Lower threshold to catch more detections
    
    print("=== Single Image Ball Detection ===")
    print(f"Model: {model_path}")
    print(f"Image: {image_path}")
    print(f"Confidence threshold: {conf_threshold}")
    print()
    
    # Perform detection
    result_image, detections = detect_ball_in_image(model_path, image_path, conf_threshold)
    
    if result_image is not None:
        # Save result
        output_path = "detection_result.jpg"
        cv2.imwrite(output_path, result_image)
        print(f"\nResult saved to: {output_path}")
        
        # Display summary
        print(f"\nDetection Summary:")
        print(f"Total detections: {len(detections)}")
        
        for i, det in enumerate(detections):
            center_x, center_y = det['center']
            conf = det['confidence']
            print(f"  Detection {i+1}: Center at ({center_x}, {center_y}), Confidence: {conf:.3f}")
    
    else:
        print("Detection failed. Please check the model and image paths.")

if __name__ == "__main__":
    main() 