from ultralytics import YOLO
import os

def train_yolo_model():
    """
    Train a YOLOv8 model for football detection
    """
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Paths
    dataset_yaml = os.path.join(project_root, "data", "yolo_dataset_augmented", "dataset.yaml")
    output_dir = os.path.join(project_root, "models")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize model 
    model = YOLO('yolov8n.pt')  # Loading the pretrained YOLOv8 nano model
    
    # Training configuration
    results = model.train(
        data=dataset_yaml,
        epochs=300,  # More epochs for better training
        imgsz=640,   # Image size
        batch=16,    # Optimal batch size for GPU
        device='cuda',  # Use GPU for maximum performance
        project=output_dir, # output directory for the model
        name='football_detector', # name of the model
        patience=50,  # Early stopping patience if no improvement after 50 epochs
        save=True, # save the model after each epoch
        save_period=10,  # Save every 10 epochs
        verbose=True, # print the training progress
        augment=True  # Enable data augmentation for better model generalization
    )
    
    # Save the final model
    model.save(os.path.join(output_dir, 'football_detector', 'best.pt')) # save the model in the output directory
    # Yolo saves automatically the best model as best.pt? need to check this!

    print(f"Training completed. Model saved to: {os.path.join(output_dir, 'football_detector')}")
    
    # Validate the model
    print("Validating the model:\n")
    metrics = model.val()

    # Print validation metrics
    print(f"Validation metrics: {metrics}")

    return model


def export_for_deployment(model_path, output_dir=None):
    """
    A function to convert bzw. export the model for Raspberry Pi deplyment.
    """
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, "models")
    # load the trained model for export
    model = YOLO(model_path)
    
    # Export to ONNX format 
    onnx_path = model.export(format='onnx', 
                            imgsz=640, # image size
                            half=True) # use half precision for smaller size
    
    print(f"Model exported to ONNX: {onnx_path}")
    
    return onnx_path

if __name__ == "__main__":
    #print("Starting YOLOv8 training for football detection:\n")
    
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Train the model
    model = train_yolo_model()
    
    # Export for deployment
    best_model_path = os.path.join(project_root, "models", "football_detector", "best.pt")
    if os.path.exists(best_model_path):
        print("\nExporting model for deployment.....")
        export_for_deployment(best_model_path)
    else:
        print(f"model notfound at {best_model_path}") 