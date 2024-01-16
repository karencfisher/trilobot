from flask import Flask, Response, render_template
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import threading

app = Flask(__name__)

# Initialize the camera only once
camera_initialized = False
camera_lock = threading.Lock()
camera = None
raw_capture = None

def initialize_camera():
    global camera_initialized
    with camera_lock:
        if not camera_initialized:
            try:
                global camera
                camera = PiCamera()
                camera.resolution = (640, 480)
                camera.framerate = 32
                global raw_capture
                raw_capture = PiRGBArray(camera)
                camera_initialized = True
            except Exception as e:
                print(f"Error initializing camera: {e}")
                # Handle the error as needed

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
    return "Remote Controls Page"

def generate_frames():
    initialize_camera()
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        img = frame.array

        # inference, add bounding boxes

        # Encode the frame as JPEG
        _, jpeg_encoded = cv2.imencode('.jpg', img)
        frame_data = jpeg_encoded.tobytes()

        # Yield the frame data as bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

        # Clear the stream for the next frame
        raw_capture.truncate(0)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
