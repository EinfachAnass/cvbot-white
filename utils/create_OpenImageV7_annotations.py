import cv2
import torch
from PIL import Image
import os
import csv
import numpy as np
from transformers import GroundingDinoProcessor, GroundingDinoForObjectDetection
from transformers import CLIPProcessor, CLIPModel

# Use ball directory from data folder
sources = "./data/ball"
output_dir = "./annot_data/output"
annotation_dir = "./annot_data/annotations"

device = "cuda" if torch.cuda.is_available() else "cpu"

gd_model_id = "IDEA-Research/grounding-dino-base"
processor = GroundingDinoProcessor.from_pretrained(gd_model_id)
gd_model = GroundingDinoForObjectDetection.from_pretrained(gd_model_id).to(device)

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()

# Constants
FOOTBALL_LABEL_ID = "201" # from OpenImagesV7 YAML for football
FOOTBALL_DISPLAY_NAME = "Football"
ANNOTATION_FILE_MAIN = annotation_dir + "/openimage_annotations.csv"
ANNOTATION_FILE_TRAIN = annotation_dir + "/train-annotations-bbox.csv"
CLASS_DESCRIPTION_FILE = annotation_dir + "/class-descriptions-boxable.csv"
THRESHOLD = 0.55
PROMPT = "ball"

def detect_regions(image, prompt=PROMPT, box_thresh=0.3):
    inputs = processor(images=image, text=prompt + ".", return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = gd_model(**inputs)

    width, height = image.size
    results = processor.post_process_grounded_object_detection(
        outputs, threshold=box_thresh, target_sizes=[(height, width)]
    )[0]

    boxes = results["boxes"].cpu().numpy()
    scores = results["scores"].cpu().numpy()
    return boxes, scores

def is_football(crop_pil, threshold=THRESHOLD):
    inputs = clip_processor(text=["a football", "not a football"],
                            images=crop_pil, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)
    return bool(probs[0][0] > threshold)

def draw_overlay(image, box, color=(0, 255, 0), alpha=0.5):
    x1, y1, x2, y2 = map(int, box)
    overlay = image.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

def write_annotations(file_path, headers, rows):
    file_exists = os.path.exists(file_path)
    write_header = True

    if file_exists:
        with open(file_path, "r", newline="") as f:
            first_line = f.readline()
            if first_line.strip() == ",".join(headers):
                write_header = False

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists or write_header:
            writer.writerow(headers)
        writer.writerows(rows)

def get_annotated_image_ids(annotation_file):
    annotated_ids = set()
    if os.path.exists(annotation_file):
        with open(annotation_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                annotated_ids.add(row["ImageID"])
    return annotated_ids

def process_image(sources, output_path, annotation_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(annotation_dir, exist_ok=True)
    annotation_rows = []

    already_annotated = get_annotated_image_ids(ANNOTATION_FILE_TRAIN)

    for filename in os.listdir(sources):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            continue
        
        image_id = os.path.splitext(filename)[0]
        if image_id in already_annotated:
            # print(f"Skipping already annotated image: {filename}")
            continue

        # print(f"Processing: {filename}")
        path = os.path.join(sources, filename)

        pil = Image.open(path).convert("RGB")
        cv_img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

        width, height = pil.size
        image_id = os.path.splitext(filename)[0]

        boxes, scores = detect_regions(pil)

        for box, score in zip(boxes, scores):
            x1, y1, x2, y2 = map(int, box)
            if x2 <= x1 or y2 <= y1:
                continue

            crop = pil.crop((x1, y1, x2, y2))
            if crop.size == 0:
                continue

            if is_football(crop):
                draw_overlay(cv_img, box)
                XMin = x1 / width
                XMax = x2 / width
                YMin = y1 / height
                YMax = y2 / height

                annotation_rows.append([
                    image_id,
                    "model-generated",
                    FOOTBALL_LABEL_ID,
                    1.0,
                    XMin, XMax, YMin, YMax,
                    0, 0, 0, 0, 0
                ])

                # print(f"Detected football in {filename} with score {score:.2f}")
                
                # uncomment to save only football images
                cv2.imwrite(os.path.join(output_dir, filename), cv_img) 
        # Uncomment to save all the images 
        cv2.imwrite(os.path.join(output_dir, filename), cv_img)

    # Write OpenImages-style annotations
    # IsOccluded ... IsInside are left 0. could be manually set.
    headers = [
        "ImageID", "Source", "LabelName", "Confidence",
        "XMin", "XMax", "YMin", "YMax",
        "IsOccluded", "IsTruncated", "IsGroupOf", "IsDepiction", "IsInside"
    ]
    for file in [ANNOTATION_FILE_MAIN, ANNOTATION_FILE_TRAIN]:
        write_annotations(file, headers, annotation_rows)

    with open(CLASS_DESCRIPTION_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([FOOTBALL_LABEL_ID, FOOTBALL_DISPLAY_NAME])

process_image(sources, output_dir, annotation_dir)
