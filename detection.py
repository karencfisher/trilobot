import cv2
import time
threshold = 0.2

configPath = 'model/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'model/frozen_inference_graph.pb'
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

with open('model/coco.names') as FILE:
    class_names = FILE.read().rstrip("\n").split("\n")

def getObjects(img, objects):
    classIds, confs, bbox = net.detect(img, confThreshold=threshold, nmsThreshold=0.2)
    objectInfo = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = class_names[classId - 1]
            # if className in objects:
            #     objectInfo.append([box, className])
        objectInfo.append([box, className])
    return objectInfo

def processImage(img):
    # inference
    try:
        object_info = getObjects(img, ['cat'])
    except Exception as e:
        print(f'Exception: {e}')

    # Markup with bounding boxes
    for index in range(len(object_info)):
        cv2.rectangle(img, object_info[index][0], color=(0, 0, 255), thickness=2)
        cv2.putText(img, str(object_info[index][1]), (object_info[index][0][0] + 5, 
                                                object_info[index][0][1] + 20), 
                                                cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)
    
    # Anything else we may want to do

    return img, object_info