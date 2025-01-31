import customtkinter
import pymongo
from pymongo import MongoClient
from PIL import Image
import threading
import datetime
import os

# Connect to MongoDB
cluster = MongoClient(
    "mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x600")
        self.title("Sacred Logs")
        self.resizable(True, True)

        # Use CTk widgets instead of vanilla tkinter
        self.textbox = customtkinter.CTkTextbox(self, wrap="word", width=700, height=500)
        self.textbox.pack(padx=20, pady=20, fill="both", expand=True)

        self.scroll = customtkinter.CTkScrollbar(self, command=self.textbox.yview)
        self.scroll.pack(side="right", fill="y")
        self.textbox.configure(yscrollcommand=self.scroll.set)

        self.display_logs()
        self.grab_set()

    def display_logs(self):
        self.textbox.delete("1.0", "end")
        if os.path.exists("database_logs.txt"):
            with open("database_logs.txt", "r") as log_file:
                self.textbox.insert("1.0", log_file.read())


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Medical Inventory")
        self.geometry("1200x800")  # Increased size for James' glory

        # Configure sacred appearance
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        # Initialize UI components
        self.setup_ui()
        self.refresh_items()
        self.start_monitoring_changes()

        # HOLY VISAGE OF JAMES
        self.setup_sacred_image()

    def setup_sacred_image(self):
        try:
            self.james_image = customtkinter.CTkImage(
                dark_image=Image.open("pictures/face7.jpg"),
                size=(800, 200)
            )
            self.image_label = customtkinter.CTkLabel(
                self,
                image=self.james_image,
                text="",
                corner_radius=20
            )
            self.image_label.grid(row=1, column=1, rowspan=4, padx=20, pady=20)
        except Exception as e:
            print(f"Machine spirit displeased: {str(e)}")

    def setup_ui(self):
        # [Keep previous UI setup code but add these enhancements]

        # Status display
        self.status_label = customtkinter.CTkLabel(self, text="System: Awaiting Command")
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="ew")

    def write_to_log(self, action, details):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {action}: {details}\n"
        with open("database_logs.txt", "a") as f:
            f.write(log_entry)
        if self.toplevel_window and self.toplevel_window.winfo_exists():
            self.toplevel_window.textbox.insert("end", log_entry)

    def refresh_items(self):
        items = [doc["Item"] for doc in collection.find()]
        self.CurrentDocumentsDropdown.configure(values=items)

    def addstuff(self):
        name = self.AddNameBox.get().strip()
        amount = self.AddAmountBox.get().strip()

        if not name or not amount:
            self.status_label.configure(text="Error: Empty fields detected!", text_color="red")
            return

        try:
            last_id = collection.find_one(sort=[("_id", -1)])["_id"]
            new_id = last_id + 1
        except:
            new_id = 1

        try:
            collection.insert_one({
                "_id": new_id,
                "Item": name,
                "Amount": int(amount)
            })
            self.write_to_log("ITEM_CREATION", f"Added {name} (ID: {new_id}) x{amount}")
            self.refresh_items()
            self.status_label.configure(text=f"Success: Added {name} x{amount}", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Database Error: {str(e)}", text_color="red")

    def update_name_amount(self):
        pass

    # [Implement similar sacred logic for updates]

    def delete_item(self):
        pass

    # [Implement proper deletion rituals]

    def start_monitoring_changes(self):
        def change_watcher():
            with collection.watch() as stream:
                for change in stream:
                    self.after(0, self.process_change, change)

        threading.Thread(target=change_watcher, daemon=True).start()

    def process_change(self, change):



# [Add holy change processing logic]

app = App()
app.mainloop()