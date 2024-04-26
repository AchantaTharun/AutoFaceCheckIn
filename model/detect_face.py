import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
from mtcnn import MTCNN

model = MTCNN()
required_size = (299, 299)

def retrieve_face(filename, face):
    face_img = cv2.imread(filename)
    box = face['box']
    face_ = face_img[max(0, box[1]):max(0, box[1] + box[3]), max(0, box[0]):max(0, box[0] + box[2])]
    face_box = cv2.resize(face_, required_size, interpolation=cv2.INTER_CUBIC)
    return np.asarray(face_box)

def detect_face(filename):
    pixels = plt.imread(filename)
    faces = model.detect_faces(pixels)
    detected_faces = []

    for face in faces:
        box = face['box']
        if box[0] >= 0 and box[1] >= 0 and box[2] > 0 and box[3] > 0:
            face_img = retrieve_face(filename, face)
            detected_faces.append(face_img)

    return np.array(detected_faces)
