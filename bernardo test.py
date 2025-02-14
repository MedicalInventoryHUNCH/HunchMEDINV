import customtkinter
import pymongo
from pymongo import MongoClient
from PIL import Image
import threading
import datetime
import os

# Connect to MongoDB
cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]
item_names = [doc["Item"] for doc in collection.find()]

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1280x720")
        self.title("Details / Logs")
        self.resizable(True, True)
        customtkinter.set_appearance_mode("dark")
        self.configure(fg_color=("#DBDBDB", "#2B2B2B"))
        self.textbox = customtkinter.CTkTextbox(
            self,
            font=("Segoe UI", 12),
            wrap="word",
            fg_color=("#FFFFFF", "#1E1E1E"),
            border_width=1,
            border_color=("#AAAAAA", "#444444")
        )
        self.textbox.pack(padx=20, pady=20, fill="both", expand=True)
        self.scrollbar = customtkinter.CTkScrollbar(
            self,
            command=self.textbox.yview,
            button_color=("#3B8ED0", "#1F6AA5")
        )
        self.scrollbar.pack(side="right", fill="y")
        self.textbox.configure(yscrollcommand=self.scrollbar.set)
        self.display_logs()

    def display_logs(self):
        log_filename = "database_logs.txt"
        if os.path.exists(log_filename):
            with open(log_filename, "r") as log_file:
                logs = log_file.read()
                self.textbox.insert("0.0", logs)
        else:
            self.textbox.insert("0.0", "No logs available.\n")
        self.grab_set()
        self.focus_force()
        self.after(200, self.release_grab)

    def release_grab(self):
        self.grab_release()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1024x600")
        self.state("zoomed")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.title("Medical Inventory System")
        self.minsize(800, 600)
        self.toplevel_window = None
        self.bind("<F11>", lambda event: self.toggle_maximize())

        # GUI elements initialization
        self.TitleLabel = customtkinter.CTkLabel(
            self, text="Medical Inventory System", text_color="White", font=("Arial", 24, "bold"))
        self.TitleLabel.grid(row=0, column=0, columnspan=3, pady=20)

        # Add Item Section
        self.AddItemFrame = customtkinter.CTkFrame(self, corner_radius=10)
        self.AddItemFrame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.AddItemLabel = customtkinter.CTkLabel(self.AddItemFrame, text="Add New Item", font=("Arial", 18))
        self.AddItemLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.AddNameBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Item Name", width=300)
        self.AddNameBox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.AddAmountBox = customtkinter.CTkEntry(
            self.AddItemFrame,
            placeholder_text="Enter Doses",
            width=300
        )
        self.AddAmountBox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        self.AddExpiry = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Expiration Date: MM/DD/YYYY", width=300)
        self.AddExpiry.grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        self.AddButton = customtkinter.CTkButton(
            self.AddItemFrame, text="Add Item", command=self.addstuff, width=150
        )
        self.AddButton.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Edit Section
        self.EditFrame = customtkinter.CTkFrame(self, corner_radius=10)
        self.EditFrame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.EditItemLabel = customtkinter.CTkLabel(self.EditFrame, text="Edit Existing Item", font=("Arial", 18))
        self.EditItemLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.CurrentDocumentsDropdown = customtkinter.CTkOptionMenu(
            self.EditFrame, values=item_names, width=200
        )
        self.CurrentDocumentsDropdown.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.EditSelectedName = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Name", width=200)
        self.EditSelectedName.grid(row=2, column=0, padx=10, pady=5)
        self.UpdateButton = customtkinter.CTkButton(
            self.EditFrame, text="Update", command=self.update_name_amount, width=100
        )
        self.UpdateButton.grid(row=5, column=0, padx=10, pady=10)
        self.EditSelectedAmount = customtkinter.CTkEntry(
            self.EditFrame,
            placeholder_text="Enter New Doses",
            width=200
        )
        self.EditSelectedAmount.grid(row=3, column=0, padx=10, pady=5)
        self.EditSelectedExpiry = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Expiration Date: MM/DD/YYYY", width=200)
        self.EditSelectedExpiry.grid(row=4, column=0, padx=10, pady=5)
        self.ViewLogsButton = customtkinter.CTkButton(
            self, text="Logs", command=self.view_logs, width=200
        )
        self.ViewLogsButton.grid(row=3, column=0, padx=20, pady=20)
        self.start_monitoring_changes()
        self.DeleteButton = customtkinter.CTkButton(
            self.EditFrame, text="Delete Item", command=self.delete_item, width=100,fg_color=("#E55353", "#CC4A4A"),hover_color=("#CC4A4A", "#B34141")
        )
        self.DeleteButton.grid(row=5, column=2, columnspan=2, padx=10, pady=10)

        # Documents Display Section
        self.DocumentFrame = customtkinter.CTkFrame(self, corner_radius=10)
        self.DocumentFrame.grid(row=1, column=1, rowspan=3, padx=20, pady=20, sticky="nsew")
        self.DocumentFrame.grid_columnconfigure(0, weight=1)
        self.DocumentFrame.grid_rowconfigure(2, weight=1)
        self.SearchFrame = customtkinter.CTkFrame(self.DocumentFrame, fg_color="transparent")
        self.SearchFrame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.SearchEntry = customtkinter.CTkEntry(
            self.SearchFrame,
            placeholder_text="Search items...",
            width=200
        )
        self.SearchEntry.grid(row=0, column=0, padx=(0, 10), pady=5)
        self.SearchEntry.bind("<Return>", lambda event: self.perform_search())
        self.SearchButton = customtkinter.CTkButton(
            self.SearchFrame,
            text="Search",
            command=self.perform_search,
            width=80
        )
        self.SearchButton.grid(row=0, column=1, padx=0, pady=5)
        self.DocumentLabel = customtkinter.CTkLabel(self.DocumentFrame, text="Current Inventory", font=("Arial", 18))
        self.DocumentLabel.grid(row=1, column=0, pady=10, sticky="n")
        self.DocumentTextbox = customtkinter.CTkTextbox(
            self.DocumentFrame,
            wrap="none",
            state="disabled",
            font=("Consolas", 12)
        )
        self.DocumentTextbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.DocumentTextbox.tag_config("highlight", background="#FE9000")
        self.refresh_document_display()

    def refresh_document_display(self):
        try:
            self.DocumentTextbox.configure(state="normal")
            self.DocumentTextbox.delete("1.0", "end")
            docs = collection.find().sort("_id", pymongo.ASCENDING)
            for doc in docs:
                doc_str = f"ID: {doc.get('_id', 'N/A')}\n"
                doc_str += f"Item: {doc.get('Item', 'Unnamed Item')}\n"
                doc_str += f"Doses: {doc.get('Doses', 0)}\n"
                expiry = doc.get('Expiry')
                if expiry:
                    try:
                        expiry_date = datetime.datetime.strptime(expiry, "%m%d%y")
                        formatted_expiry = expiry_date.strftime("%m/%d/%Y")
                        doc_str += f"Expiry: {formatted_expiry}\n"
                    except ValueError:
                        doc_str += f"Expiry: {expiry}\n"
                doc_str += "-" * 40 + "\n"
                self.DocumentTextbox.insert("end", doc_str)
            self.DocumentTextbox.configure(state="disabled")
        except Exception as e:
            print(f"Error refreshing document display: {e}")
            self.DocumentTextbox.configure(state="disabled")

    def write_to_log(self, action, details):
        log_filename = "database_logs.txt"
        with open(log_filename, "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%m/%d/%y")
            log_file.write(f"[{timestamp}] {action}: {details}\n")

    def addstuff(self):
        name = self.AddNameBox.get().strip()
        amount = self.AddAmountBox.get().strip()
        expiry_str = self.AddExpiry.get().strip()

        if name and amount:
            expiry_date_str = None
            expiry_date = None
            if expiry_str:
                try:
                    expiry_date = datetime.datetime.strptime(expiry_str, "%m/%d/%Y")
                    expiry_date_str = expiry_date.strftime("%m/%d/y")
                except ValueError:
                    print("Invalid expiry date format. Please use MM/DD/YYYY.")
                    return

            try:
                last_doc = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
                new_id = 1 if last_doc is None else last_doc['_id'] + 1
                doc1 = {"_id": new_id, "Item": name, "Doses": int(amount)}
                if expiry_date_str:
                    doc1["Expiry"] = expiry_date_str

                collection.insert_one(doc1)
                log_message = f"Added item '{name}' with ID {new_id}, doses {amount}"
                if expiry_date:
                    log_message += f", expiry {expiry_date.strftime('%m/%d/%Y')}"
                self.write_to_log("Add", log_message)
                print(f"Item added successfully with ID {new_id}!")
                self.refresh_dropdown()
                self.refresh_document_display()
            except Exception as e:
                print(f"Error adding item: {e}")
        else:
            print("Please fill in both name and doses fields.")

    def update_name_amount(self):
        original_name = self.CurrentDocumentsDropdown.get()
        selected_item = self.CurrentDocumentsDropdown.get()
        new_name = self.EditSelectedName.get().strip()
        new_amount = self.EditSelectedAmount.get().strip()
        new_expiry = self.EditSelectedExpiry.get().strip()

        update_fields = {}
        if new_name:
            update_fields["Item"] = new_name
        if new_amount:
            try:
                update_fields["Doses"] = int(new_amount)
            except ValueError:
                print("Doses must be an integer.")
                return
        if new_expiry:
            try:
                expiry_date = datetime.datetime.strptime(new_expiry, "%m/%d/%Y")
                expiry_date_str = expiry_date.strftime("%m/%d/y")
                update_fields["Expiry"] = expiry_date_str
            except ValueError:
                print("Invalid expiry date format. Please use MM/DD/YYYY.")
                return

        if selected_item and update_fields:
            try:
                result = collection.update_one({"Item": selected_item}, {"$set": update_fields})
                updated_fields_list = []
                for key, value in update_fields.items():
                    if key == "Expiry":
                        try:
                            date_obj = datetime.datetime.strptime(value, "%m/%d/%y")
                            formatted_value = date_obj.strftime("%m/%d/%Y")
                            updated_fields_list.append(f"{key}: {formatted_value}")
                        except:
                            updated_fields_list.append(f"{key}: {value}")
                    else:
                        updated_fields_list.append(f"{key}: {value}")
                updated_fields_str = ", ".join(updated_fields_list)
                self.write_to_log("Update", f"Updated item '{original_name}' to {updated_fields_str}.")
                if result.modified_count > 0:
                    print(f"Updated '{selected_item}' to {update_fields}")
                    self.refresh_dropdown()
                    self.refresh_document_display()
                else:
                    print("No item was updated.")
            except Exception as e:
                self.write_to_log("Error", f"Failed to update item '{original_name}': {e}")
                print(f"Error updating item: {e}")
        else:
            print("Please select an item and change at least one field.")

    # Remaining methods remain unchanged (refresh_dropdown, view_logs, monitor_changes, etc.)

app = App()
app.mainloop()