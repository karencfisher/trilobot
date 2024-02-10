import cv2


THREASHOLD = 0.2

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
    classIds, confs, bbox = net.detect(img, confThreshold=THREASHOLD, nmsThreshold=0.2)
    objectInfo = []
    if len(classIds) != 0:
        for classId, _, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = class_names[classId - 1]
            # if className in objects:
            #     objectInfo.append([box, className])
        objectInfo.append([box, className])
    return objectInfo
