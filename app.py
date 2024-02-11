from flask import Flask, Response, render_template, request, jsonify
import cv2
import time
import threading
from multiprocessing import Process, Queue, Value
from sensors import getObjects, processImage, video_loop, sensor_loop
from motor import dispatch_command
import json
import os
import signal


# Controller globals
SPEED = 0.7
THRESHOLD = 20
app = Flask(__name__)

# Initialize the robot only once
robot_initialized = False
robot_lock = threading.Lock()
video_process = None
video_que = None
video_flag = None
motor_process = None
sensor_process = None
command_que = None
distance = None
run_flag = None

def initialize_robot():
    global robot_initialized
    with robot_lock:
        if not robot_initialized:
            global run_flag
            global video_process
            global video_que
            global distance
            global motor_process
            global command_que

            distance = Value('i', 0)
            run_flag = Value('i', 1)
            video_que = Queue()
            command_que = Queue()

            # initialize video_process
            video_process = Process(target=video_loop, args=(video_que, distance, run_flag))
            video_process.start()

            # initialize sensor process
            sensor_process = Process(target=sensor_loop, args=(distance, THRESHOLD, 
                                                               command_que, run_flag))
            sensor_process.start()

            # Initialize motor process
            motor_process = Process(target=dispatch_command, args=(command_que, 
                                                                   run_flag, SPEED))
            motor_process.start()
            robot_initialized = True

def generate_frames():
    initialize_robot()
    time.sleep(.1)
    while run_flag.value:
        if video_que is None or video_que.empty():
            continue
        img = video_que.get(False)    

        # Encode the frame as JPEG
        _, jpeg_encoded = cv2.imencode('.jpg', img)
        frame_data = jpeg_encoded.tobytes()

        # Yield the frame data as bytes
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

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
    command = request.args.get("command")
    if command == "exit":
        # push "exit" command
        run_flag.value = 0
        motor_process.join()
        sensor_process.join()
        video_process.join()
        status = {'status': 'exit'}
        os.kill(os.getpid(), signal.SIGINT)
    else:
        command_que.put(command)
        status = {'status': command}
    return jsonify(json.dumps(status))
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
