import cv2
import os
import time

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
# classFile = os.path.join(current_dir, "yolov3/coco.names")
# classes = open(classFile).read().strip().split('\n')
# np.random.seed(42)
# colors = np.random.randint(0, 255, size=(len(classes), 3), dtype='uint8')
# configPath = os.path.join(current_dir, "yolov3/yolov3.cfg")
# weightsPath = os.path.join(current_dir, "yolov3/yolov3.weights")
# net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
# ln = net.getLayerNames()
# print(net.getUnconnectedOutLayers())
# ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

# For SSD
def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects: 
                objectInfo.append([box,className])
                if draw:
                    if classId == 1:
                        color = (0,255,0)
                    else:
                        color = (0,0,255)
                    cv2.rectangle(img, box, color=color, thickness=2)
                    cv2.putText(img, classNames[classId-1].upper(), (box[0], box[1] - 3),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 1)
                    cv2.putText(img, str(round(confidence*100, 2)), (box[0] + 3, box[1] + 15),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 1)
    
    return img,objectInfo

# For YOLO
def post_process(img, outputs, conf):
    H, W = img.shape[:2]

    boxes = []
    confidences = []
    classIDs = []

    for output in outputs:
        scores = output[5:]
        classID = np.argmax(scores)
        confidence = scores[classID]
        if confidence > conf:
            x, y, w, h = output[:4] * np.array([W, H, W, H])
            p0 = int(x - w//2), int(y - h//2)
            p1 = int(x + w//2), int(y + h//2)
            boxes.append([*p0, int(w), int(h)])
            confidences.append(float(confidence))
            classIDs.append(classID)
            # cv.rectangle(img, p0, p1, WHITE, 1)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf, conf-0.1)
    if len(indices) > 0:
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            color = [int(c) for c in colors[classIDs[i]]]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            text = "{}: {:.4f}".format(classes[classIDs[i]], confidences[i])
            cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

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
    
    # Detect objects
    result, objectInfo = getObjects(frame,0.5,0.1)
    # blob = cv2.dnn.blobFromImage(frame, 1/255.0, (480, 640), swapRB=True, crop=False)
    # net.setInput(blob)
    # start_infer = time.time()
    # outputs = net.forward(ln)
    # end_infer = time.time()
    # outputs = np.vstack(outputs)
    # post_process(frame, outputs, 0.5)
    

    # Display the frame
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
    # Drop frames
    for i in range(5):
        ret, frame = cap.read()
        
    end_time = time.perf_counter()
    
    print("fps: %.2f" % (1/(end_time - start_time)))

# Release the video stream and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()