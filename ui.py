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
        self.geometry("1200x1000")
        self.title("Details / Logs")
        self.resizable(True, True)

        # Add a Scrollable Textbox
        self.textbox = customtkinter.CTkTextbox(self)
        self.textbox.pack(padx=20, pady=20, fill="both", expand=True)

        # Display logs from file
        self.display_logs()

    def display_logs(self):
        log_filename = "database_logs.txt"
        if os.path.exists(log_filename):
            with open(log_filename, "r") as log_file:
                logs = log_file.read()
                self.textbox.insert("0.0", logs)
        else:
            self.textbox.insert("0.0", "No logs available.\n")
        # Enable scrolling
        self.scrollbar = customtkinter.CTkScrollbar(self, command=self.textbox.yview)
        self.textbox.configure(yscrollcommand=self.scrollbar.set)
        # Place the scrollbar to the right of the textbox
        self.scrollbar.pack(side="right", fill="y")
        self.grab_set()
        self.focus_force()
        self.after(200, self.release_grab)

    def release_grab(self):
        self.grab_release()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Set appearance
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.title("Medical Inventory")
        self.geometry("800x700")

        self.toplevel_window = None

        # Title Label
        self.TitleLabel = customtkinter.CTkLabel(
            self, text="Medical Inventory System", text_color="White", font=("Arial", 24, "bold")
        )
        self.TitleLabel.grid(row=0, column=0, columnspan=3, pady=20)

        # Add Item Section
        self.AddItemFrame = customtkinter.CTkFrame(self, corner_radius=10)
        self.AddItemFrame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.AddItemLabel = customtkinter.CTkLabel(self.AddItemFrame, text="Add New Item", font=("Arial", 18))
        self.AddItemLabel.grid(row=0, column=0, columnspan=2, pady=10)

        self.AddNameBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Item Name", width=300)
        self.AddNameBox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.AddAmountBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Amount", width=300)
        self.AddAmountBox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        # Expiration Date Entry Box
        self.AddExpiry = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Expiration Date: DD/MM/YYYY", width=300)
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

        # Change Name
        self.EditSelectedName = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Name", width=200)
        self.EditSelectedName.grid(row=2, column=0, padx=10, pady=5)

        self.UpdateButton = customtkinter.CTkButton(
            self.EditFrame, text="Update", command=self.update_name_amount, width=200
        )
        self.UpdateButton.grid(row=5, column=1, padx=10, pady=10)

        # Change Amount
        self.EditSelectedAmount = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Amount", width=200)
        self.EditSelectedAmount.grid(row=3, column=0, padx=10, pady=5)

        self.EditSelectedExpiry = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Expiration Date", width=200)
        self.EditSelectedExpiry.grid(row=4, column=0, padx=10, pady=5)

        # James' Picture (gone but not forgotten)

        self.ViewLogsButton = customtkinter.CTkButton(
            self, text="Logs", command=self.view_logs, width=200
        )
        self.ViewLogsButton.grid(row=3, column=0, padx=20, pady=20)

        self.start_monitoring_changes()

        self.DeleteButton = customtkinter.CTkButton(
            self.EditFrame, text="Delete Item", command=self.delete_item, width=100
        )
        self.DeleteButton.grid(row=5, column=0, columnspan=2, padx=10, pady=10)


    def write_to_log(self, action, details):
        log_filename = "database_logs.txt"
        with open(log_filename, "a") as log_file:
            # Log date only (YYYY-MM-DD)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
            log_file.write(f"[{timestamp}] {action}: {details}\n")

    def addstuff(self):
        name = self.AddNameBox.get().strip()
        amount = self.AddAmountBox.get().strip()
        expiry_str = self.AddExpiry.get().strip()

        if name and amount:
            expiry_date_str = None
            if expiry_str:
                try:
                    # Parse the input date and reformat it as a string
                    expiry_date = datetime.datetime.strptime(expiry_str, "%d/%m/%Y")
                    expiry_date_str = expiry_date.strftime("%Y-%m-%d")
                except ValueError:
                    print("Invalid expiry date format. Please use DD/MM/YYYY.")
                    return

            try:
                # Get the highest current ID
                last_doc = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
                new_id = 1 if last_doc is None else last_doc['_id'] + 1

                # Build the document; store the expiry as a formatted string if provided
                doc1 = {"_id": new_id, "Item": name, "Amount": int(amount)}
                if expiry_date_str:
                    doc1["Expiry"] = expiry_date_str

                collection.insert_one(doc1)
                self.write_to_log("Add", f"Added item '{name}' with ID {new_id}, amount {amount}" +
                                        (f", expiry {expiry_date_str}" if expiry_date_str else ""))
                print(f"Item added successfully with ID {new_id}!")
                self.refresh_dropdown()
            except Exception as e:
                print(f"Error adding item: {e}")
        else:
            print("Please fill in both name and amount fields.")

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
                update_fields["Amount"] = int(new_amount)
            except ValueError:
                print("Amount must be an integer.")
                return
        if new_expiry:
            try:
                expiry_date = datetime.datetime.strptime(new_expiry, "%d/%m/%Y")
                expiry_date_str = expiry_date.strftime("%Y-%m-%d")
                update_fields["Expiry"] = expiry_date_str
            except ValueError:
                print("Invalid expiry date format. Please use DD/MM/YYYY.")
                return

        if selected_item and update_fields:
            try:
                result = collection.update_one({"Item": selected_item}, {"$set": update_fields})
                updated_fields_list = ", ".join([f"{key}: {value}" for key, value in update_fields.items()])
                self.write_to_log("Update", f"Updated item '{original_name}' to {updated_fields_list}.")
                if result.modified_count > 0:
                    print(f"Updated '{selected_item}' to {update_fields}")
                    self.refresh_dropdown()
                else:
                    print("No item was updated.")
            except Exception as e:
                self.write_to_log("Error", f"Failed to update item '{original_name}': {e}")
                print(f"Error updating item: {e}")
        else:
            print("Please select an item and change at least one field.")

    def refresh_dropdown(self):
        global item_names
        item_names = [doc["Item"] for doc in collection.find()]
        self.CurrentDocumentsDropdown.configure(values=item_names)

    def view_logs(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)
        else:
            self.toplevel_window.focus_force()

    def monitor_changes(self):
        change_pipeline = [{"$match": {"operationType": "update"}}]
        try:
            with collection.watch(pipeline=change_pipeline, full_document="updateLookup") as stream:
                for change in stream:
                    updated_id = change["documentKey"].get("_id")
                    updated_fields = change["updateDescription"]["updatedFields"]
                    new_amount = updated_fields.get("Amount")
                    new_name = change["fullDocument"].get("Item")
                    previous_amount = change["fullDocument"].get("Doses", new_amount)
                    print(f"ID: {updated_id}, Name: {new_name}, Previous Amount: {previous_amount}, New Amount: {new_amount}")
        except Exception as e:
            print(f"Error in change stream: {e}")

    def delete_item(self):
        selected_item = self.CurrentDocumentsDropdown.get()
        if selected_item:
            try:
                result = collection.delete_one({"Item": selected_item})
                if result.deleted_count > 0:
                    self.write_to_log("Delete", f"Deleted item '{selected_item}'.")
                    print(f"Item '{selected_item}' was successfully deleted!")
                    self.refresh_dropdown()
                else:
                    print(f"Item '{selected_item}' was not found.")
            except Exception as e:
                self.write_to_log("Error", f"Failed to delete item '{selected_item}': {e}")
                print(f"Error deleting item: {e}")
        else:
            print("No item selected for deletion.")

    def start_monitoring_changes(self):
        monitor_thread = threading.Thread(target=self.monitor_changes, daemon=True)
        monitor_thread.start()

app = App()
app.mainloop()
