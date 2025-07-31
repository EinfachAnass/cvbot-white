# CVBot White - Football Detection Robot

A computer vision system for real-time football detection using YOLOv8 and autonomous robot control via the CVBot framework.

## Prerequisites

- Python 3.12+
- CUDA-compatible GPU (recommended for training)

### Option 1: Conda Environment

```bash
# Clone the repository
git clone https://github.com/EinfachAnass/cvbot-white.git
cd cvbot-white

# Create and activate environment
conda env create -f environment.yml
conda activate catandball
```

### Option 2: Using venv 

```bash
# Create virtual environment
python -m venv cvbot-env

# Activate environment
# On Linux/Mac:
source cvbot-env/bin/activate
# On Windows:
cvbot-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Training Workflow

The training process consists of **4 main steps**:

### **Step 1: Automatic Annotation**
Generate annotations automatically:
```bash
# Annotate images using GroundingDINO + CLIP
python utils/create_OpenImageV7_annotations.py
```
**What it does:**
- Uses **GroundingDINO** for object detection with text prompts
- Uses **CLIP** for football classification
- Generates OpenImageV7 format annotations
- Creates `data/annotations/openimage_annotations.csv`
- Saves annotated images to `data/annotated_images/`

**Note:** We deleted the original images due to space constraints. You can:
- Add your own football images to `data/images/`
- Use existing annotations if you have them
- The script automatically skips already annotated images

### **Step 2: Data Conversion**
Convert OpenImageV7 annotations to YOLO format:
```bash
python utils/convert_to_yolo.py
```
**What it does:**
- Reads OpenImageV7 CSV annotations
- Converts bounding boxes to YOLO format
- Creates `data/yolo_dataset/` with images and labels
- Generates `dataset.yaml` configuration

### **Step 3: Data Augmentation**
Augment the dataset with realistic transformations:
```bash
python utils/augementation.py
```
**What it does:**
- Creates 3 augmented versions of each image
- Applies realistic transformations (lighting, shadows, noise, blur)
- Generates `data/yolo_dataset_augmented/`


### **Step 4: Model Training**
Train YOLOv8 model on the augmented dataset:
```bash
python utils/train_yolo.py
```
**What it does:**
- Loads YOLOv8 nano pretrained model
- Trains for 300 epochs with early stopping
- Saves best model to `models/football_detector/`
- Provides validation metrics


### Environment Configuration

Create a `.env` file for robot connection:

```env
HOST=your_robot_host
PORT=your_robot_port
KEY=your_robot_key
```

## Training

### Training Configuration

The training script (`utils/train_yolo.py`) includes:

- **Model**: YOLOv8 nano (yolov8n.pt)
- **Epochs**: 300
- **Batch Size**: 16
- **Image Size**: 640x640
- **Device**: CUDA (GPU)
- **Augmentation**: Enabled
- **Early Stopping**: 50 epochs patience

### Expected Outputs

After training, you'll have:
```
models/ football_detector/
    best.pt          # Best trained model
    results.png      # Training results
    confusion_matrix.png
```

## Robot Control

### PID Control for Autonomous Movement

The main robot control script combines computer vision with PID control for autonomous football tracking:

```bash
# Run the autonomous football tracking robot
python pid.py
```

**What it does:**
- Loads the trained YOLOv8 football detection model
- Captures video from the robot's camera
- Detects football position in real-time
- Uses PID control to track and follow the football
- Controls robot movement (forward/backward, left/right, rotation)
- Saves annotated frames showing detection and control parameters


**Control Logic:**
- Robot steers left/right based on football position
- Moves forward when football is far away
- Stops when football is close
- Moves backward when football is too close
