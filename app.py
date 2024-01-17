from flask import Flask, Response, render_template
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import threading
from detection import getObjects

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
    frame_count = 0
    start_time = time.time()
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        img = frame.array

        # inference, add bounding boxes
        try:
            object_info = getObjects(img, ['cat'])
        except Exception as e:
            print(f'Exception: {e}')

        for index in range(len(object_info)):
            cv2.rectangle(img, object_info[index][0], color=(0, 0, 255), thickness=2)
            cv2.putText(img, str(object_info[index][1]), (object_info[index][0][0], 
                                                 object_info[index][0][1] - 20), 
                                                 cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
