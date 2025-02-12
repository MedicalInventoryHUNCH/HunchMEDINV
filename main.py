import customtkinter
import pymongo
from pymongo import MongoClient
from PIL import Image
import threading
import datetime
import os
import face_recognition
import cv2
import nfc
import ndef
import time

# Connect to MongoDB
cluster = MongoClient(
    "mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]
collection1 = db["astro"]  # For face recognition data
item_names = [doc["Item"] for doc in collection.find()]


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1200x1000")
        self.title("Details / Logs")
        self.resizable(True, True)

        self.textbox = customtkinter.CTkTextbox(self)
        self.textbox.pack(padx=20, pady=20, fill="both", expand=True)
        self.display_logs()

    def display_logs(self):
        log_filename = "database_logs.txt"
        if os.path.exists(log_filename):
            with open(log_filename, "r") as log_file:
                logs = log_file.read()
                self.textbox.insert("0.0", logs)
        else:
            self.textbox.insert("0.0", "No logs available.\n")
        self.scrollbar = customtkinter.CTkScrollbar(self, command=self.textbox.yview)
        self.textbox.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.grab_set()
        self.focus_force()
        self.after(200, self.release_grab)

    def release_grab(self):
        self.grab_release()


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.nfc_reader = nfc.ContactlessFrontend('usb')
        self.cap = cv2.VideoCapture(0)
        self.known_faces = self.load_known_faces()

        self.setup_gui()
        self.start_background_threads()

    def setup_gui(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.title("Medical Inventory")
        self.geometry("800x700")

        # [Keep all the original GUI setup code from the first script]
        # ... (same as original GUI setup code)

    def load_known_faces(self):
        known_faces = []
        try:
            for i in range(6):
                img = face_recognition.load_image_file(f"pictures/face{i}.jpg")
                encoding = face_recognition.face_encodings(img)[0]
                known_faces.append(encoding)
            return known_faces
        except Exception as e:
            print(f"Error loading faces: {e}")
            return []

    def start_background_threads(self):
        face_thread = threading.Thread(target=self.face_recognition_loop, daemon=True)
        face_thread.start()

        nfc_thread = threading.Thread(target=self.nfc_monitor_loop, daemon=True)
        nfc_thread.start()

    def face_recognition_loop(self):
        while True:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                face_locations = face_recognition.face_locations(frame)
                if face_locations:
                    face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
                    matches = face_recognition.compare_faces(self.known_faces, face_encoding)
                    if True in matches:
                        first_match_index = matches.index(True)
                        print(f"Recognized face ID: {first_match_index}")
            except Exception as e:
                print(f"Face recognition error: {e}")
            time.sleep(1)

    def nfc_monitor_loop(self):
        while True:
            try:
                tag = self.nfc_reader.connect(rdwr={'on-connect': lambda tag: False})
                if tag.ndef:
                    records = tag.ndef.records
                    self.process_nfc_tag(records)
            except Exception as e:
                print(f"NFC error: {e}")
            time.sleep(1)

    def process_nfc_tag(self, records):
        try:
            record = str(records[0])
            if "NFCNASAMED" in record:
                parts = record.split('%')
                if len(parts) >= 3:
                    item_id = int(parts[2])
                    collection.update_one({"_id": item_id}, {"$inc": {"Amount": -1}})
                    self.write_to_log("NFC Scan", f"Decremented item ID {item_id}")
                    self.refresh_dropdown()
        except Exception as e:
            print(f"Error processing NFC tag: {e}")

    # [Keep all the original database methods from the first script]
    # ... (same as original database methods)

    def destroy(self):
        self.cap.release()
        self.nfc_reader.close()
        super().destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()