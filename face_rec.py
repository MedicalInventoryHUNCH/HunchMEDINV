import face_recognition
import cv2
import time

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        exit(":(")

    #img = face_recognition.load_image_file(frame)
    imgencode = face_recognition.face_encodings(frame)[0]

    img2 = face_recognition.load_image_file("pictures/face2.jpg")
    imgencode2 = face_recognition.face_encodings(img2)[0]

    img3 = face_recognition.load_image_file("pictures/face3.jpg")
    imgencode3 = face_recognition.face_encodings(img3)[0]

    img4 = face_recognition.load_image_file("pictures/face4.jpg")
    imgencode4 = face_recognition.face_encodings(img4)[0]

    img5 = face_recognition.load_image_file("pictures/face5.jpg")
    imgencode5 = face_recognition.face_encodings(img5)[0]

    img6 = face_recognition.load_image_file("pictures/face6.jpg")
    imgencode6 = face_recognition.face_encodings(img6)[0]

    img7 = face_recognition.load_image_file("pictures/face7.jpg")
    imgencode7 = face_recognition.face_encodings(img7)[0]

    known_faces = [
        imgencode2, imgencode3, imgencode4, imgencode5, imgencode6, imgencode7
    ]

    if len(imgencode) > 0 and len(imgencode2) > 0:
        results = face_recognition.compare_faces(known_faces, imgencode)
        break
    else:
        pass
print(results)

truthy_indices = [index for index, value in enumerate(results) if bool(value)]

print(truthy_indices)