from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
from detection import getObjects
from trilobot import read_distance
from math import ceil


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

def video_loop(video_que, distance, video_flag, detect=False):
    frame_count = 0
    start_time = time.time()

    # Initialize camera
    camera = PiCamera()
    camera.resolution = (304, 240)
    camera.framerate = 32
    raw_capture = PiRGBArray(camera)
    time.sleep(.1)

    # loop through frames
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        if not video_flag.value:
            break
        if detect:
            raw_img = frame.array
            img, _ = processImage(raw_img)
        else:
            img = frame.array

        # Annotate with frame rate
        frame_count += 1
        fps = round(frame_count / (time.time() - start_time), 2)
        cv2.putText(img, str(fps) + " FPS", (20, 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)

        # annotate distance
        cv2.putText(img, str(distance.value) + " cm", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)
               
        video_que.put(img)
        raw_capture.truncate(0)

def sensor_loop(distance, threshold, motor_que, run_flag):
    obstacle_detected = False
    while run_flag:
        distance.value = ceil(read_distance())
        if distance.value <= threshold:
            motor_que.put("turn-right")
            obstacle_detected = True
        elif obstacle_detected:
            motor_que.put("forward")
            obstacle_detected = False
