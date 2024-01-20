import cv2
import os
import time
from ultralytics import YOLO
import torch
from dotenv import dotenv_values

# URL of the video stream
config = dotenv_values(".env")
IP = config["BROKER_IP"]
video_url = "http://" + IP + ":8000/stream.mjpg"

# Setup neural network
model = YOLO('yolov8n.pt', verbose=False)  # pretrained YOLOv8n model
if torch.cuda.is_available():
    model.cuda()
    print("Using GPU")
else:
    print("CUDA not available, using CPU instead")

# Open the video stream
cap = cv2.VideoCapture(video_url)
if not cap.isOpened():
    print("Error: Unable to open video stream")
    exit()

while True:
    start_time = time.time()
    # Read a frame from the video stream
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame")
        break
    #frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
    # print("max: %.2f, min: %.2f" % (np.max(frame), np.min(frame))) 
    # max=255, min=0
    
    # Detect objects
    outputs = model(frame,verbose=False)
    plot = outputs[0].plot()
    #plot = cv2.resize(outputs[0].plot(font_size=20), None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    #print(type(outputs[0].boxes))
    # Display the frame
    cv2.imshow('Frame', plot)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    end_time = time.time()
    
    # Drop frames
    # for i in range(2):
        # ret, frame = cap.read()
    
    print("fps: %.2f" % (1/(end_time - start_time)))

# Release the video stream and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()