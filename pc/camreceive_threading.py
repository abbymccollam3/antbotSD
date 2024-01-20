import cv2
import os
import time
import numpy as np
import threading
from queue import Queue

# URL of the video stream
video_url = "http://100.70.12.182:8000/stream.mjpg"


# Setup neural network
current_dir = os.getcwd()
classNames = []
classFile = os.path.join(current_dir, "ssd_mobilenet/coco.names")
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")
configPath = os.path.join(current_dir, "ssd_mobilenet/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt")
weightsPath = os.path.join(current_dir, "ssd_mobilenet/frozen_inference_graph.pb")
net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(480,640)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def detect(q, thres, nms, draw=True, objects=[]):
    while True:
        img = q.get()
        classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
        cv2.imshow('Frame', img)
        if len(objects) == 0: objects = classNames
        objectInfo =[]
        if len(classIds) != 0:
            for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                className = classNames[classId - 1]
                if className in objects: 
                    objectInfo.append([box,className])
                    if draw:
                        cv2.rectangle(img, box, color=(0,255,0), thickness=2)
                        cv2.putText(img, classNames[classId-1].upper(), (box[0], box[1] + 30),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
                        cv2.putText(img, str(round(confidence*100, 2)), (box[0], box[1] + 60),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)

# Open the video stream
cap = cv2.VideoCapture(video_url)
if not cap.isOpened():
    print("Error: Unable to open video stream")
    exit()

# Threading stuff
q = Queue(maxsize=1)
lock = threading.Lock()
thread = threading.Thread(target=detect, args=(q, 0.5, 0.5))
thread.daemon = True  # Set the thread as daemon so it terminates when the main thread terminates
thread.start()

while True:
    start_time = time.time()
    # Read a frame from the video stream
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame")
        break
        
    # print("max: %.2f, min: %.2f" % (np.max(frame), np.min(frame))) 
    # max=255, min=0
    
    # Pass data to object detector
    q.put(frame.copy())

    # Display the frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    end_time = time.time()
    print("fps: %.2f" % (1/(end_time - start_time)))

# Release the video stream and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()