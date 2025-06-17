import os
import csv
import cv2
import torch
from ultralytics import YOLO
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# Get model from YOLO (Download automatically if not present)
yolo_model = YOLO("yolo12x.pt")
# Get model CLIP (Download automatically if not present)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()

# Constants
FOOTBALL_LABEL_ID = "201" # from OpenImagesV7 YAML for football
FOOTBALL_DISPLAY_NAME = "Football"
ANNOTATION_FILE_MAIN = "./../annotations/openimage_annotations.csv"
ANNOTATION_FILE_TRAIN = "./../annotations/train-annotations-bbox.csv"
CLASS_DESCRIPTION_FILE = "./../annotations/class-descriptions-boxable.csv"

def is_football(crop_pil):
    inputs = clip_processor(text=["a football", "not a football"], images=crop_pil, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)
    return probs[0][0] > 0.7

def draw_bbox(image, box, label, color=(0, 255, 0)):
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    cv2.putText(image, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def draw_overlay(image, box, color=(0, 255, 0), alpha=0.5):
    x1, y1, x2, y2 = map(int, box)
    overlay = image.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

def process_images(sources, output_dir, annotation_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(annotation_dir, exist_ok=True)
    annotation_rows = []

    for filename in os.listdir(sources):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        path = os.path.join(sources, filename)
        image = cv2.imread(path)
        if image is None:
            continue
        orig = image.copy()
        h, w = image.shape[:2]
        image_id = os.path.splitext(filename)[0]

        results = yolo_model(image)[0]
        for box, cls_id in zip(results.boxes.xyxy, results.boxes.cls):
            if yolo_model.names[int(cls_id)] != "sports ball":
                continue

            x1, y1, x2, y2 = map(int, box.tolist())
            crop = orig[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            crop_pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            if is_football(crop_pil):
                draw_overlay(image, (x1, y1, x2, y2))
                draw_bbox(image, (x1, y1, x2, y2), "football")

                XMin = x1 / w
                XMax = x2 / w
                YMin = y1 / h
                YMax = y2 / h

                annotation_rows.append([
                    image_id,
                    "model-generated",
                    FOOTBALL_LABEL_ID,
                    1.0,
                    XMin, XMax, YMin, YMax,
                    0, 0, 0, 0, 0
                ])

        # Save modified image
        cv2.imwrite(os.path.join(output_dir, filename), image)

    # Write OpenImages-style annotations
    # IsOccluded ... IsInside are left 0. could be manually set.
    headers = [
        "ImageID", "Source", "LabelName", "Confidence",
        "XMin", "XMax", "YMin", "YMax",
        "IsOccluded", "IsTruncated", "IsGroupOf", "IsDepiction", "IsInside"
    ]
    for file in [ANNOTATION_FILE_MAIN, ANNOTATION_FILE_TRAIN]:
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(annotation_rows)

    with open(CLASS_DESCRIPTION_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([FOOTBALL_LABEL_ID, FOOTBALL_DISPLAY_NAME])

# Run
sources = "./../data/ball"
output_dir = "outputsYOLO12x_clip_annotated"
annotation_dir = "./../annotations"
process_images(sources, output_dir, annotation_dir)
