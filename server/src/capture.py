import cv2
import time
from flask import Blueprint, Response
from firebase import Firebase

config = {
    "apiKey": "AIzaSyCfTKQ-5sDNvN3QfC6S4oqeKOnbEv7AxzE",
    "authDomain": "iot-smart-home-door-lock-7ccc9.firebaseapp.com",
    "databaseURL": "https://iot-smart-home-door-lock-7ccc9.firebaseio.com",
    "projectId": "iot-smart-home-door-lock-7ccc9",
    "storageBucket": "iot-smart-home-door-lock-7ccc9.appspot.com",
    "messagingSenderId": "513607106040",
    "appId": "1:513607106040:web:d627644390357454e76a0d"
}

firebase = Firebase(config)
storage = firebase.storage()
bp_capture = Blueprint('capture', __name__)
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


def capture(rfid, status):
    count = 0
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    try:
        while cap.isOpened():
            ret, image = cap.read()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)
            if ret:
                for (x, y, w, h) in face_rects:
                    cv2.rectangle(image, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)
                    roi_gray = gray[y:y+h, x:x+w]
                    cv2.imwrite(f"dataset/{rfid}.{str(count)}.jpg", roi_gray)
                    count += 1

                frame = cv2.imencode('.jpg', image)[1].tobytes()
                yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
                time.sleep(0.1)
            else:
                break

            if status == 'cancel':
                break
            elif count > 30:
                break
    except Exception as e:
        print(e)


@bp_capture.route('/api/capture/<rfid>/<status>')
def video_feed(rfid, status):
    return Response(capture(rfid, status), mimetype='multipart/x-mixed-replace; boundary=frame')
