import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
from mtcnn import MTCNN
from PIL import Image
from io import BytesIO
import base64
import os


model = MTCNN()
required_size = (299, 299)

if not os.path.exists("test_images"):
    os.makedirs("test_images")

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


def retrieve_face_from_frame(frame, face):
    box = face['box']
    face_ = frame[max(0, box[1]):max(0, box[1] + box[3]), max(0, box[0]):max(0, box[0] + box[2])]
    face_box = cv2.resize(face_, required_size, interpolation=cv2.INTER_CUBIC)
    return np.asarray(face_box)

def detect_face_from_stream(frame_data):
    try:
        base64_data = frame_data.split(",")[1]

        image_bytes = base64.b64decode(base64_data)

        nparr = np.frombuffer(image_bytes, np.uint8)

        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        faces = model.detect_faces(rgb_image)

        detected_faces = []

        if faces:
            for i, face in enumerate(faces):
                box = face['box']
                if box[0] >= 0 and box[1] >= 0 and box[2] > 0 and box[3] > 0:
                    face_img = retrieve_face_from_frame(rgb_image, face)
                    
                    detected_faces.append(face_img)

                    filename = f"test_images/face_{i}.jpg"
                    cv2.imwrite(filename, cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR))
            
            return np.array(detected_faces)
        else:
            print("No faces detected in the image")

    except Exception as e:
        print("Error:", e)
