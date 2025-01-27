import face_recognition
import cv2
import time

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        exit(":(")

    cv2.imwrite("pictures/video.jpg", frame)
    time.sleep(0.5)


