import customtkinter
import pymongo
from pymongo import MongoClient
from PIL import Image
import threading

# Connect to MongoDB
cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]
item_names = [doc["Item"] for doc in collection.find()]

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = customtkinter.CTkLabel(self, text="")
        self.label.pack(padx=20, pady=20)
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

        self.AddNameBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Item Name")
        self.AddNameBox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.AddAmountBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Amount")
        self.AddAmountBox.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        self.AddButton = customtkinter.CTkButton(
            self.AddItemFrame, text="Add Item", command=self.addstuff, width=150
        )
        self.AddButton.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

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
        self.EditSelectedName = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Name")
        self.EditSelectedName.grid(row=2, column=0, padx=10, pady=5)

        self.ChangeNameAmountButton = customtkinter.CTkButton(
            self.EditFrame, text="Update Name &/or Amount", command=self.update_name_amount, width=200
        )
        self.ChangeNameAmountButton.grid(row=3, column=1, padx=10, pady=10)

        # Change Amount
        self.EditSelectedAmount = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Amount")
        self.EditSelectedAmount.grid(row=3, column=0, padx=10, pady=5)

        # James' Picture (IMPORTANT PART)
        self.James = customtkinter.CTkImage(
            dark_image=Image.open("pictures/face7.jpg"),
            size=(1000, 250)
        )
        self.PicOfJames = customtkinter.CTkLabel(
            self,
            image=self.James,
            text="",
            corner_radius=20
        )
        self.PicOfJames.grid(row=1, column=2, padx=10, pady=10, rowspan=2)

        self.ViewLogsButton = customtkinter.CTkButton(
            self, text="Logs Placeholder", command=self.view_logs, width=200
        )
        self.ViewLogsButton.grid(row=3, column=0, padx=20, pady=20)

        self.start_monitoring_changes()

        self.DeleteButton = customtkinter.CTkButton(
            self.EditFrame, text="Delete Item", command=self.delete_item, width=100
        )
        self.DeleteButton.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def addstuff(self):
        name = self.AddNameBox.get().strip()
        amount = self.AddAmountBox.get().strip()

        if name and amount:
            try:
                # Get the highest current ID
                last_doc = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
                new_id = 1 if last_doc is None else last_doc['_id'] + 1

                doc1 = {"_id": new_id, "Item": name, "Amount": int(amount)}
                collection.insert_one(doc1)
                print(f"Item added successfully with ID {new_id}!")
                self.refresh_dropdown()
            except Exception as e:
                print(f"Error adding item: {e}")
        else:
            print("Please fill name and amount fields.")

    def update_name_amount(self):
        selected_item = self.CurrentDocumentsDropdown.get()
        new_name = self.EditSelectedName.get().strip()
        new_amount = self.EditSelectedAmount.get().strip()

        update_fields = {}
        if new_name:
            update_fields["Item"] = new_name
        if new_amount:
            try:
                update_fields["Amount"] = int(new_amount)
            except ValueError:
                print("Amount must be an integer.")
                return

        if selected_item and update_fields:
            try:
                result = collection.update_one({"Item": selected_item}, {"$set": update_fields})
                if result.modified_count > 0:
                    print(f"Updated '{selected_item}' with {update_fields}")
                    self.refresh_dropdown()
                else:
                    print("No item was updated.")
            except Exception as e:
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
                    previous_amount = change["fullDocument"].get("Amount", new_amount)
                    print(f"ID: {updated_id}, Name: {new_name}, Previous Amount: {previous_amount}, New Amount: {new_amount}")
        except Exception as e:
            print(f"Error in change stream: {e}")

    def delete_item(self):
        selected_item = self.CurrentDocumentsDropdown.get()
        if selected_item:
            try:
                result = collection.delete_one({"Item": selected_item})
                if result.deleted_count > 0:
                    print(f"Item '{selected_item}' was successfully deleted!")
                    self.refresh_dropdown()
                else:
                    print(f"Item '{selected_item}' was not found.")
            except Exception as e:
                print(f"Error deleting item: {e}")
        else:
            print("No item selected for deletion.")

    def start_monitoring_changes(self):
        monitor_thread = threading.Thread(target=self.monitor_changes, daemon=True)
        monitor_thread.start()

app = App()
app.mainloop()