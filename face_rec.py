import face_recognition
import cv2
import time
import ndef
import nfc
from ndef import TextRecord
import pymongo
from pymongo import MongoClient

cap = cv2.VideoCapture(0)

imgencode = imgencode2 = imgencode3 = imgencode4 = imgencode5 = imgencode6 = imgencode7 = None

img2 = face_recognition.load_image_file("pictures/face2.jpg")
img3 = face_recognition.load_image_file("pictures/face3.jpg")
img4 = face_recognition.load_image_file("pictures/face4.jpg")
img5 = face_recognition.load_image_file("pictures/face5.jpg")
img6 = face_recognition.load_image_file("pictures/face6.jpg")
img7 = face_recognition.load_image_file("pictures/face7.jpg")


while True:
    ret, frame = cap.read()
    if not ret:
        exit(":(")

    try:
        imgencode = face_recognition.face_encodings(frame)[0]

        imgencode2 = face_recognition.face_encodings(img2)[0]

        imgencode3 = face_recognition.face_encodings(img3)[0]

        imgencode4 = face_recognition.face_encodings(img4)[0]

        imgencode5 = face_recognition.face_encodings(img5)[0]

        imgencode6 = face_recognition.face_encodings(img6)[0]

        imgencode7 = face_recognition.face_encodings(img7)[0]
    except IndexError:
        exit("No face detected.")

    known_faces = [
        imgencode2, imgencode3, imgencode4, imgencode5, imgencode6, imgencode7
    ]
    results = face_recognition.compare_faces(known_faces, imgencode)
    break

print(results)

true_stuff = [index for index, value in enumerate(results) if bool(value)]

print(true_stuff)




