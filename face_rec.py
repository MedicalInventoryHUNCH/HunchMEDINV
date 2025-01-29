import face_recognition
import cv2
import time
import ndef
import nfc
from pymongo import MongoClient
import os


mongo_uri = os.getenv("MONGO_URI")  # Fetch the URI from the environment variables
cluster = MongoClient(mongo_uri)
db = cluster["Inventory"]
collection = db["astro"]

clf = nfc.ContactlessFrontend('usb')

def load_known_faces():
    known_faces = []
    try:
        # Load all reference faces
        for i in range(2, 8):
            img = face_recognition.load_image_file(f"pictures/face{i}.jpg")
            encoding = face_recognition.face_encodings(img)[0]
            known_faces.append(encoding)
        return known_faces
    except FileNotFoundError:
        print("Error: One or more face images not found in 'pictures' directory")
        exit(1)
    except IndexError:
        print("Error: No face detected in one or more reference images")
        exit(1)


def capture_and_compare(cap, known_faces):
    """Capture a frame and compare with known faces"""
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read from webcam")
        return None

    try:
        # Get encoding of face in current frame
        current_face_encoding = face_recognition.face_encodings(frame)[0]

        # Compare with known faces
        results = face_recognition.compare_faces(known_faces, current_face_encoding)

        # Get indices of matching faces
        matches = [index for index, value in enumerate(results) if bool(value)]
        return matches

    except IndexError:
        print("No face detected in camera frame")
        return None

def idnumber(tag_data):
    if "NFCNASAMED" in str(tag_data):
        print("scanned" + str(tag_data))
        meds = str(tag_data)
        splitmeds = meds.split('%')
        print(int(splitmeds[2]))
        intmeds = int(splitmeds[2])
        return intmeds

    else:
        print("med unknown tag")

def nfc_read():
    id_num = idnumber()
    if id_num is None:
        print("nettspend hate is forced")
        return

    else:
        tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        tag_data = ndef.record if tag.ndef else None


        collection.update_many({"_id": id_num}, {"$inc": {"Amount": -1}})
        time.sleep(2)

        print("ready")
        if tag_data is None:
            print("no tag data")
            return

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    try:
        # Load known faces
        known_faces = load_known_faces()

        # Capture and process one frame
        matches = capture_and_compare(cap, known_faces)

        if matches is not None:
            print(f"Face matches with indices: {matches}")

    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
