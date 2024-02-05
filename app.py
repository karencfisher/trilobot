from flask import Flask, Response, render_template, request, jsonify
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import threading
from multiprocessing import Process, Queue
from detection import getObjects, processImage
from control import dispatch_command
import json
import os
import signal

app = Flask(__name__)

# Initialize the camera only once
camera_initialized = False
camera_lock = threading.Lock()
camera = None
raw_capture = None

# Controller globals
SPEED = 0.7
robot_initialized = False
robot_lock = threading.Lock()
robot_process = None
command_que = None

def initialize_camera():
    global camera_initialized
    with camera_lock:
        if not camera_initialized:
            try:
                global camera
                camera = PiCamera()
                camera.resolution = (300, 225)
                camera.framerate = 32
                global raw_capture
                raw_capture = PiRGBArray(camera)
                camera_initialized = True
            except Exception as e:
                print(f"Error initializing camera: {e}")

def initialize_robot(speed):
    # Lock to only allow a single thread to run this code at one time
    with robot_lock:
        global robot_initialized
        # Only initialize the processs to control Trilobot once in a thread
        if not robot_initialized:
            global robot_process
            global command_que
            # queue to push commands to the control process
            command_que = Queue()
            # Initialize and start the process
            robot_process = Process(target=dispatch_command, args=(command_que, 
                                                                   SPEED))
            robot_process.start()
            robot_initialized = True

def generate_frames():
    initialize_camera()
    frame_count = 0
    start_time = time.time()
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        # perform inference on image
        raw_img = frame.array
        img, _ = processImage(raw_img)

        # Markup with frame rate
        frame_count += 1
        fps = round(frame_count / (time.time() - start_time), 2)
        cv2.putText(img, str(fps) + " FPS", (20, 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)      

        # Encode the frame as JPEG
        _, jpeg_encoded = cv2.imencode('.jpg', img)
        frame_data = jpeg_encoded.tobytes()

        # Yield the frame data as bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

        # Clear the stream for the next frame
        raw_capture.truncate(0)

# Route to load the webpage
@app.route('/')
def index():
    return render_template('index.html')

# Route for streaming video frames
@app.route('/video/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for remote controls (you can adapt this as needed)
@app.route('/controls')
def remote_controls():
    initialize_robot(SPEED)
    command = request.args.get("command")
    if command == "exit":
        # push "exit" command
        command_que.put("exit")
        # wait for control process to exit
        robot_process.join()
        status = {'status': 'exit'}
        os.kill(os.getpid(), signal.SIGINT)
    else:
        command_que.put(command)
        status = {'status': command}
    return jsonify(json.dumps(status))
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
