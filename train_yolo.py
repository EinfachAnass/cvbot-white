from ultralytics import YOLO
import os

def train_yolo_model():
    """
    Train a YOLOv8 model for football detection
    """
    # Paths
    dataset_yaml = "../data/yolo_dataset/dataset.yaml"
    output_dir = "../models"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize model 
    model = YOLO('yolov8n.pt')  # Loading the pretrained YOLOv8 nano model
    
    # Training configuration
    results = model.train(
        data=dataset_yaml,
        epochs=100,  # Number of epochs
        imgsz=640,   # Image size
        batch=16,    # Batch size
        device='cpu',  # Use CPU for training or 'cuda' for GPU
        project=output_dir, # output directory for the model
        name='football_detector', # name of the model
        patience=20,  # Early stopping patience if no improvement after 20 epochs
        save=True, # save the model after each epoch
        save_period=10,  # Save every 10 epochs
        verbose=True # print the training progress
    )
    
    # Save the final model
    model.save(os.path.join(output_dir, 'football_detector', 'best_model.pt')) # save the model in the output directory


    print(f"Training completed. Model saved to: {os.path.join(output_dir, 'football_detector')}")
    
    # Validate the model
    print("Validating the model:\n")
    metrics = model.val()

    # Print validation metrics
    print(f"Validation metrics: {metrics}")

    return model