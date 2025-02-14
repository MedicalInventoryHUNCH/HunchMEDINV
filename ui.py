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

        # Modern styling
        customtkinter.set_appearance_mode("dark")
        self.configure(fg_color=("#DBDBDB", "#2B2B2B"))

        # Textbox styling
        self.textbox = customtkinter.CTkTextbox(
            self,
            font=("Segoe UI", 12),
            wrap="word",
            fg_color=("#FFFFFF", "#1E1E1E"),
            border_width=1,
            border_color=("#AAAAAA", "#444444")
        )
        self.textbox.pack(padx=20, pady=20, fill="both", expand=True)

        # Scrollbar setup in __init__ to ensure only one exists
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

        self.geometry("1024x600")  # Default size if not maximized


        self.grid_columnconfigure(0, weight=1)  # Left column (input fields)
        self.grid_columnconfigure(1, weight=3)  # Right column (document display)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Set appearance
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.title("Medical Inventory System")
        self.minsize(800, 600)


        self.toplevel_window = None

        self.bind("<F11>", lambda event: self.toggle_maximize())


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

        self.AddAmountBox = customtkinter.CTkEntry(
            self.AddItemFrame,
            placeholder_text="Enter Doses",  # Changed
            width=300
        )
        self.AddAmountBox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        # Expiration Date Entry Box
        self.AddExpiry = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Expiration Date: MM/DD/YY", width=300)
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
            self.EditFrame, text="Update", command=self.update_name_amount, width=100
        )
        self.UpdateButton.grid(row=5, column=0, padx=10, pady=10)

        # Change Amount
        self.EditSelectedAmount = customtkinter.CTkEntry(
            self.EditFrame,
            placeholder_text="Enter New Doses",  # Changed
            width=200
        )
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
            self.EditFrame, text="Delete Item", command=self.delete_item, width=100,fg_color=("#E55353", "#CC4A4A"),hover_color=("#CC4A4A", "#B34141")


        )
        self.DeleteButton.grid(row=5, column=2, columnspan=2, padx=10, pady=10)

        # Documents Display Section (modified to include search)
        self.DocumentFrame = customtkinter.CTkFrame(self, corner_radius=10)
        self.DocumentFrame.grid(row=1, column=1, rowspan=3, padx=20, pady=20, sticky="nsew")
        self.DocumentFrame.grid_columnconfigure(0, weight=1)
        self.DocumentFrame.grid_rowconfigure(2, weight=1)  # Textbox row

        # Search Frame
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

        # Document Label
        self.DocumentLabel = customtkinter.CTkLabel(self.DocumentFrame, text="Current Inventory", font=("Arial", 18))
        self.DocumentLabel.grid(row=1, column=0, pady=10, sticky="n")

        # Document Textbox
        self.DocumentTextbox = customtkinter.CTkTextbox(
            self.DocumentFrame,
            wrap="none",
            state="disabled",
            font=("Consolas", 12)
        )
        self.DocumentTextbox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        # Original color was #FFFACD - changed to less intense #FFF3A0
        self.DocumentTextbox.tag_config("highlight", background="#FE9000")  # Changed from #FE9000 #F7F7FF

        # Initial display of documents
        self.refresh_document_display()

    def refresh_document_display(self):
        """Fetches and displays all documents from the database"""
        try:
            # Temporarily enable the textbox to update content
            self.DocumentTextbox.configure(state="normal")
            self.DocumentTextbox.delete("1.0", "end")

            # Get all documents and format them
            docs = collection.find().sort("_id", pymongo.ASCENDING)
            for doc in docs:
                # Use get() with default values for safety
                doc_str = f"ID: {doc.get('_id', 'N/A')}\n"
                doc_str += f"Item: {doc.get('Item', 'Unnamed Item')}\n"
                doc_str += f"Amount: {doc.get('Amount', 0)}\n"

                # Handle optional expiration date
                expiry = doc.get('Expiry')
                if expiry:
                    doc_str += f"Expiry: {expiry}\n"

                doc_str += "-" * 40 + "\n"
                self.DocumentTextbox.insert("end", doc_str)

            # Disable the textbox again after update
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
            if expiry_str:
                try:
                    # Parse the input date and reformat it as a string
                    expiry_date = datetime.datetime.strptime(expiry_str, "%m/%d/%y")
                    expiry_date_str = expiry_date.strftime("%m/%d/%y")
                except ValueError:
                    print("Invalid expiry date format. Please use MM/DD/YY.")
                    return

            try:
                # Get the highest current ID
                last_doc = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
                new_id = 1 if last_doc is None else last_doc['_id'] + 1

                # Build the document; store the expiry as a formatted string if provided
                doc1 = {"_id": new_id, "Item": name, "Doses": int(amount)}  # Changed
                if expiry_date_str:
                    doc1["Expiry"] = expiry_date_str

                collection.insert_one(doc1)
                self.write_to_log("Add", f"Added item '{name}' with ID {new_id}, doses {amount}")  # Changed
                (f", expiry {expiry_date_str}" if expiry_date_str else "")
                print(f"Item added successfully with ID {new_id}!")
                self.refresh_dropdown()
                self.refresh_document_display()  # Add this line

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
                update_fields["Doses"] = int(new_amount)  # Changed
            except ValueError:
                print("Amount must be an integer.")
                return
        if new_expiry:
            try:
                expiry_date = datetime.datetime.strptime(new_expiry, "%m/%d/%y")
                expiry_date_str = expiry_date.strftime("%m/%d/%y")
                update_fields["Expiry"] = expiry_date_str
            except ValueError:
                print("Invalid expiry date format. Please use MM/DD/YY.")
                return

        if selected_item and update_fields:
            try:
                result = collection.update_one({"Item": selected_item}, {"$set": update_fields})
                updated_fields_list = ", ".join([f"{key}: {value}" for key, value in update_fields.items()])
                self.write_to_log("Update", f"Updated item '{original_name}' to {updated_fields_list}.")
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
                    new_amount = updated_fields.get("Doses")  # Changed
                    new_name = change["fullDocument"].get("Item")
                    previous_amount = change["fullDocument"].get("Doses", new_amount)  # Changed
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
                    self.refresh_document_display()
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

    def monitor_changes(self):
        change_pipeline = [{"$match": {"operationType": {"$in": ["insert", "update", "delete"]}}}]
        try:
            with collection.watch(pipeline=change_pipeline) as stream:
                for change in stream:
                    # Schedule GUI update in main thread
                    self.after(5, self.refresh_document_display)
        except Exception as e:
            print(f"Error in change stream: {e}")



    def perform_search(self):
        """Highlight documents containing the search query"""
        query = self.SearchEntry.get().strip().lower()
        self.DocumentTextbox.configure(state="normal")
        self.DocumentTextbox.tag_remove("highlight", "1.0", "end")

        if query:
            start_idx = "1.0"
            while True:
                # Find next occurrence of the separator line
                sep_start = self.DocumentTextbox.search("-" * 40, start_idx, stopindex="end")
                if not sep_start:
                    # Check remaining text after last separator
                    block_text = self.DocumentTextbox.get(start_idx, "end-1c")
                    if any(query in line.lower() for line in block_text.split("\n")):
                        self.DocumentTextbox.tag_add("highlight", start_idx, "end-1c")
                    break

                # Get end of separator line
                sep_end = self.DocumentTextbox.index(f"{sep_start} lineend")
                # Check block from start_idx to sep_end (includes separator)
                block_text = self.DocumentTextbox.get(start_idx, sep_end)
                if any(query in line.lower() for line in block_text.split("\n")):
                    self.DocumentTextbox.tag_add("highlight", start_idx, sep_end)

                # Move to next block
                start_idx = self.DocumentTextbox.index(f"{sep_end} + 1 char")

        self.DocumentTextbox.configure(state="disabled")

    def refresh_document_display(self):
        """Fetches and displays all documents (with search reset)"""
        try:
            self.DocumentTextbox.configure(state="normal")
            self.DocumentTextbox.delete("1.0", "end")

            # Get documents from database
            docs = collection.find().sort("_id", pymongo.ASCENDING)
            for doc in docs:
                doc_str = f"ID: {doc.get('_id', 'N/A')}\n"
                doc_str += f"Item: {doc.get('Item', 'Unnamed Item')}\n"
                doc_str += f"Doses: {doc.get('Doses', 0)}\n"  # Changed
                if "Expiry" in doc:
                    doc_str += f"Expiry: {doc['Expiry']}\n"
                doc_str += "-" * 40 + "\n"
                self.DocumentTextbox.insert("end", doc_str)

            # Reset search
            self.SearchEntry.delete(0, "end")
            self.DocumentTextbox.tag_remove("highlight", "1.0", "end")

        except Exception as e:
            print(f"Error refreshing documents: {e}")
        finally:
            self.DocumentTextbox.configure(state="disabled")


app = App()
app.mainloop()