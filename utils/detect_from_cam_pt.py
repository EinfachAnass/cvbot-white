import cv2
from ultralytics import YOLO
import time

# Load the trained YOLOv8 model
model = YOLO('/home/student/cvbot-white/models/football_detector/best.pt')

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Could not open camera!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab the frame")
        break
    # Run the inference
    start_time = time.time()
    results = model(frame)
    inference_time = time.time() - start_time

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Print center of the ball and inference time
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = box
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        print(f"Ball center: ({center_x}, {center_y}), Inference time: {inference_time:.3f}s")

    cv2.imshow("YOLOv8 Football Detection", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() 