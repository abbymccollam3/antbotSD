import cv2
import os
import time
import torch
import numpy as np

num_detections = 10

# URL of the video stream
video_url = "http://100.70.7.113:8000/stream.mjpg"

current_dir = os.getcwd()
classNames = []
classFile = os.path.join(current_dir, "ssd_mobilenet/coco.names")
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

# Setup neural network
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.cuda()

# Open the video stream
cap = cv2.VideoCapture(video_url)
if not cap.isOpened():
    print("Error: Unable to open video stream")
    exit()

while True:
    start_time = time.perf_counter()
    # Read a frame from the video stream
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame")
        break
        
    # print("max: %.2f, min: %.2f" % (np.max(frame), np.min(frame))) 
    # max=255, min=0
    
    # Convert frame to PyTorch tensor
    frame_tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0  # Convert to CHW format and normalize
    frame_tensor = frame_tensor[None, :, :, :]

    # Move frame tensor to CUDA device
    frame_tensor = frame_tensor.cuda()
    
    # Detect objects
    results = model(frame_tensor)

    # Example for first detection
    # bounding_box = results[0, 0, :4]
    # objectness_score = results[0, 0, 4]
    # class_probabilities = results[0, 0, 5:]
    
    # top_prediction = torch.argmax(results[0, :, 4])
    top_predictions = torch.topk(results[0, :, 4], k=num_detections).indices
    top_probabilities = results[0, top_predictions, 5:]
    top_ids = torch.argmax(top_probabilities, dim=1)
    bbox = results[0, top_predictions, :4].cpu().numpy().astype(int)
    # label = classNames[top_ids]
    scores = top_probabilities[torch.arange(len(top_ids)), top_ids].cpu().numpy()
    for i in range(num_detections):
        cv2.rectangle(frame, (bbox[i,0], bbox[i,1]), (bbox[i,2], bbox[i,3]), (0, 255, 0), 2)
        cv2.putText(frame, f'{classNames[top_ids[i]]}: {float(scores[i]):.2f}', (bbox[i,0], bbox[i,1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('Camera feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
    end_time = time.perf_counter()
    
    print("fps: %.2f" % (1/(end_time - start_time)))

# Release the video stream and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()