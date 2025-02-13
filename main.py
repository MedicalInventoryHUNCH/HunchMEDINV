import threading
import time
import datetime
import os
from PIL import Image

import face_recognition
import cv2
import nfc
import ndef
import pymongo
from pymongo import MongoClient
import customtkinter

# MongoDB Setup
cluster = MongoClient(
    "mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]
collection_astro = db["astro"]

# Global configuration
TAG_DEDUP_TIME = 2
recently_scanned_tags = {}


class FaceNFCThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.clf = nfc.ContactlessFrontend('usb')
        self.cap = cv2.VideoCapture(0)
        self.known_faces = self.load_known_faces()

    def load_known_faces(self):
        known_faces = []
        try:
            for i in range(9):
                img = face_recognition.load_image_file(f"pictures/face{i}.jpg")
                encoding = face_recognition.face_encodings(img)[0]
                known_faces.append(encoding)
            return known_faces
        except (FileNotFoundError, IndexError) as e:
            print(f"Error loading faces: {e}")
            return []

    def capture_and_compare(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        try:
            face_encoding = face_recognition.face_encodings(frame)[0]
            results = face_recognition.compare_faces(self.known_faces, face_encoding)
            return [i for i, match in enumerate(results) if match]
        except IndexError:
            return None

    def nfc_read(self):
        tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
        if not tag.ndef:
            return None

        records = tag.ndef.records
        if "NFCNASAMED" in str(records):
            parts = str(records).split('%')
            return int(parts[2]) if len(parts) > 2 else None
        return None

    def run(self):
        while self.running:
            try:
                matches = self.capture_and_compare()
                tag_id = self.nfc_read()

                if matches and tag_id:
                    current_time = time.time()
                    if tag_id in recently_scanned_tags:
                        if current_time - recently_scanned_tags[tag_id] < TAG_DEDUP_TIME:
                            continue
                    recently_scanned_tags[tag_id] = current_time

                    # Update database
                    collection.update_one({"_id": tag_id}, {"$inc": {"Amount": -1}})
                    collection_astro.update_one(
                        {"_id": matches[0]},
                        {"$inc": {f"Amount_{tag_id}": 1}}
                    )
                    print(f"Updated: Face {matches[0]} scanned tag {tag_id}")

            except Exception as e:
                print(f"Error in FaceNFC thread: {e}")

            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.cap.release()
        self.clf.close()


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1200x1000")
        self.title("Logs")
        self.textbox = customtkinter.CTkTextbox(self)
        self.textbox.pack(padx=20, pady=20, fill="both", expand=True)
        self.display_logs()

    def display_logs(self):
        if os.path.exists("database_logs.txt"):
            with open("database_logs.txt") as f:
                self.textbox.insert("0.0", f.read())


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.face_nfc_thread = FaceNFCThread()
        self.title("Medical Inventory System")
        self.geometry("800x700")
        self._setup_ui()
        self.start_monitoring_changes()

    def _setup_ui(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        # GUI elements setup (same as original)
        self.TitleLabel = customtkinter.CTkLabel(
            self, text="Medical Inventory System", font=("Arial", 24, "bold"))
        self.TitleLabel.grid(row=0, column=0, columnspan=3, pady=20)

        # Add remaining UI components from original GUI script
        # ... [Include all the UI setup code from the original GUI script here]

        self.ViewLogsButton = customtkinter.CTkButton(
            self, text="View Logs", command=self.view_logs)
        self.ViewLogsButton.grid(row=3, column=0, padx=20, pady=20)

    def view_logs(self):
        ToplevelWindow(self)

    def write_to_log(self, action, details):
        with open("database_logs.txt", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
            f.write(f"[{timestamp}] {action}: {details}\n")

    def start_monitoring_changes(self):
        thread = threading.Thread(target=self._monitor_changes, daemon=True)
        thread.start()

    def _monitor_changes(self):
        with collection.watch() as stream:
            for change in stream:
                print(f"Database change detected: {change}")

    def on_closing(self):
        self.face_nfc_thread.stop()
        self.face_nfc_thread.join()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.face_nfc_thread.start()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()