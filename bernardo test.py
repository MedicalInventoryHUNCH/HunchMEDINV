import customtkinter
import pymongo
from pymongo import MongoClient
from PIL import Image
import threading
import tkinter as tk
from tkinter import scrolledtext

# Connect to MongoDB
cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]
item_names = [doc["Item"] for doc in collection.find()]

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x400")
        self.title("Database Logs")

        self.log_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=20)
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.grab_set()
        self.focus_force()

    def update_logs(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.title("Medical Inventory")
        self.geometry("800x700")
        self.toplevel_window = None

        self.TitleLabel = customtkinter.CTkLabel(self, text="Medical Inventory System", text_color="White", font=("Arial", 24, "bold"))
        self.TitleLabel.grid(row=0, column=0, columnspan=3, pady=20)

        # Add Item Section
        self.AddItemFrame = customtkinter.CTkFrame(self, corner_radius=10)
        self.AddItemFrame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.AddNameBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Item Name")
        self.AddNameBox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.AddAmountBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Amount")
        self.AddAmountBox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        self.AddButton = customtkinter.CTkButton(self.AddItemFrame, text="Add Item", command=self.addstuff, width=150)
        self.AddButton.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Logs Button
        self.ViewLogsButton = customtkinter.CTkButton(self, text="View Logs", command=self.view_logs, width=200)
        self.ViewLogsButton.grid(row=3, column=0, padx=20, pady=20)

        # Picture of James
        self.James = customtkinter.CTkImage(dark_image=Image.open("pictures/face7.jpg"), size=(1000, 250))
        self.PicOfJames = customtkinter.CTkLabel(self, image=self.James, text="", corner_radius=20)
        self.PicOfJames.grid(row=1, column=2, padx=10, pady=10, rowspan=2)

        self.start_monitoring_changes()

    def addstuff(self):
        name = self.AddNameBox.get().strip()
        amount = self.AddAmountBox.get().strip()
        if name and amount:
            try:
                last_doc = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
                new_id = 1 if last_doc is None else last_doc['_id'] + 1
                doc1 = {"_id": new_id, "Item": name, "Amount": int(amount)}
                collection.insert_one(doc1)
                self.log_message(f"Added item: {name}, Amount: {amount}")
                self.refresh_dropdown()
            except Exception as e:
                self.log_message(f"Error adding item: {e}")

    def view_logs(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)
        else:
            self.toplevel_window.focus_force()

    def log_message(self, message):
        if self.toplevel_window is not None and self.toplevel_window.winfo_exists():
            self.toplevel_window.update_logs(message)

    def monitor_changes(self):
        change_pipeline = [{"$match": {"operationType": {"$in": ["insert", "update", "delete"]}}}]
        try:
            with collection.watch(pipeline=change_pipeline, full_document="updateLookup") as stream:
                for change in stream:
                    operation = change["operationType"]
                    if operation == "insert":
                        doc = change["fullDocument"]
                        self.log_message(f"New item added: {doc['Item']} (Amount: {doc['Amount']})")
                    elif operation == "update":
                        updated_fields = change["updateDescription"]["updatedFields"]
                        item_name = change["fullDocument"]["Item"]
                        self.log_message(f"Updated {item_name}: {updated_fields}")
                    elif operation == "delete":
                        deleted_id = change["documentKey"]["_id"]
                        self.log_message(f"Deleted item with ID: {deleted_id}")
        except Exception as e:
            self.log_message(f"Error in change stream: {e}")

    def start_monitoring_changes(self):
        monitor_thread = threading.Thread(target=self.monitor_changes, daemon=True)
        monitor_thread.start()

app = App()
app.mainloop()
