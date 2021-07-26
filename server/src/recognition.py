from flask import Blueprint, Response
import cv2

bp_recognition = Blueprint('recognition', __name__)
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('models/model.yml')
font = cv2.FONT_HERSHEY_SIMPLEX

def recognition():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while cap.isOpened():
        ret, image = cap.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)
        if ret:
            for (x, y, w, h) in face_rects:
                cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)
                ids, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                print(f'{ids} + {confidence}')
                if (confidence < 30):
                    # id = names[id]
                    confidence = "  {0}%".format(round(100 - confidence))
                else:
                    id = "unknown"
                    confidence = "  {0}%".format(round(100 - confidence))
                
                cv2.putText(image, str(ids), (x+5,y-5), font, 1, (255,255,255), 2)
                cv2.putText(image, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
            frame = cv2.imencode('.jpg', image)[1].tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'

        else:
            break

    cap.release()


@bp_recognition.route('/api/recognition')
def video_feed():
    return Response(recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')
