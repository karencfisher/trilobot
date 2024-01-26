from flask import Flask, Response, render_template, request, jsonify
import threading
from multiprocessing import Process, Queue
import json
import os
import signal
from trilobot import *


app = Flask(__name__)
SPEED = 0.7
robot_initialized = False
robot_lock = threading.Lock()
robot_process = None
command_que = None

def initialize_robot(speed):
    global robot_initialized
    with robot_lock:
        if not robot_initialized:
            global robot_process
            global command_que
            command_que = Queue()
            robot_process = Process(target=dispatch_command, args=(command_que, 
                                                                   SPEED))
            robot_process.start()
            robot_initialized = True

def dispatch_command(que, speed):
    tbot = Trilobot()
    print(tbot, que)
    while True:
        if not que.empty():
            command = que.get()
            print(f'Command: {command}')
            if command == "exit":
                tbot.stop()
                break
            elif command == "forward":
                tbot.forward(speed)
            elif command == "reverse":
                tbot.backward(speed)
            elif command == "left":
                tbot.turn_left(speed)
            elif command == "right":
                tbot.turn_right(speed)
            else:
                tbot.stop()

# Route to load the webpage
@app.route('/')
def index():
    return render_template('index2.html')

# Route for remote controls (you can adapt this as needed)
@app.route('/controls')
def remote_controls():
    initialize_robot(SPEED)
    command = request.args.get("command")
    if command == "exit":
        command_que.put("exit")
        robot_process.join()
        status = {'status': 'exit'}
        os.kill(os.getpid(), signal.SIGINT)
    else:
        command_que.put(command)
        status = {'status': command}
    return jsonify(json.dumps(status))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

