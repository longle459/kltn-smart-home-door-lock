from flask import Blueprint, jsonify
import cv2
import os
import numpy as np
from PIL import Image
from firebase import Firebase

config = {
    
}

bp_training = Blueprint('training', __name__)
firebase = Firebase(config)
storage = firebase.storage()
img_dir = "dataset"
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


def getImageAndLabels(img_dir):
    imagePaths = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
    faceSamples = []
    labels = []

    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')
        id_img = int(os.path.split(imagePath)[-1].split(".")[0])
        faces = detector.detectMultiScale(img_numpy)
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y+h, x:x+w])
            labels.append(id_img)
    return faceSamples, labels

directory_model = 'models/model.yml'

@bp_training.route('/api/training')
def train_model():
    try:
        print("\nFace training. please wait...")
        faces, ids = getImageAndLabels(img_dir)
        recognizer.train(faces, np.array(ids))
        if os.path.isfile(directory_model) == True:
            os.remove(directory_model)
            recognizer.write(directory_model)
            print("\nTraining success !")
            print("\n{0} faces are learned.".format(len(np.unique(ids))))
            storage.child('model.yml').put(directory_model)
            print('Uploaded the model')
            return jsonify({'success': True}), 200
        else:
            print('No model')
            recognizer.write(directory_model)
            print("\nTraining success !")
            storage.child('model.yml').put(directory_model)
            print('Uploaded the model')
            print("\n{0} faces are learned.".format(len(np.unique(ids))))
            return jsonify({'success': True}), 200
    except Exception as e:
        print(e)
