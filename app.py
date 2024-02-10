from flask import Flask, Response, render_template, request, jsonify
import cv2
import time
import threading
from multiprocessing import Process, Queue, Value
from camera import getObjects, processImage, video_loop
from control import dispatch_command
import json
import os
import signal

app = Flask(__name__)

# Initialize the camera only once
camera_initialized = False
camera_lock = threading.Lock()
video_process = None
video_que = None
video_flag = None

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
            global video_flag
            global video_process
            global video_que
            video_que = Queue()
            video_flag = Value('i', 1)
            video_process = Process(target=video_loop, args=(video_que, video_flag, True))
            video_process.start()
            camera_initialized = True

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
    time.sleep(.1)
    while video_flag.value:
        if video_que is None or video_que.empty():
            continue
        img = video_que.get(False)    

        # Encode the frame as JPEG
        _, jpeg_encoded = cv2.imencode('.jpg', img)
        frame_data = jpeg_encoded.tobytes()

        # Yield the frame data as bytes
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
    video_process.join()

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
        video_flag.value = 0
        status = {'status': 'exit'}
        os.kill(os.getpid(), signal.SIGINT)
    else:
        command_que.put(command)
        status = {'status': command}
    return jsonify(json.dumps(status))
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
