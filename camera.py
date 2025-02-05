from picamera2 import Picamera2
import cv2
import numpy as np
from detection import getObjects


def processImage(img):
    # inference
    try:
        img = np.asarray(img, dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (304, 240))[:,:,:3]
        object_info = getObjects(img, ['cat'])
    except Exception as e:
        print(f'Exception: {e}')

    # Markup with bounding boxes
    for index in range(len(object_info)):
        x, y, w, h = object_info[index][0]
        img = cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(img, str(object_info[index][1]), (object_info[index][0][0] + 5, 
                                                object_info[index][0][1] + 20), 
                                                cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 0, 0), 2)
    
    # Anything else we may want to do

    return img, object_info

def video_loop(video_que, video_flag, detect=False):
    # Initialize the camera with libcamera
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration())
    camera.start()

    while True:
        if not video_flag.value:
            break

        frame = camera.capture_array()  # Capture frame
        
        if detect:
            img, _ = processImage(frame)
        else:
            img = cv2.cvtColor(frame, cv2.COLOR_BGRRGB)

        video_que.put(img)
    camera.stop()
