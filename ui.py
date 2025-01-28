import customtkinter
import pymongo
from pymongo import MongoClient

# Connect to MongoDB
cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]
item_names = [doc["Item"] for doc in collection.find()]

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Set appearance
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        # Window title and size
        self.title("Medical Inventory")
        self.geometry("800x600")

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

        self.AddIdBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter ID")
        self.AddIdBox.grid(row=1, column=0, padx=10, pady=5)

        self.AddNameBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Item Name")
        self.AddNameBox.grid(row=1, column=1, padx=10, pady=5)

        self.AddAmountBox = customtkinter.CTkEntry(self.AddItemFrame, placeholder_text="Enter Amount")
        self.AddAmountBox.grid(row=2, column=0, padx=10, pady=5)

        self.AddButton = customtkinter.CTkButton(
            self.AddItemFrame, text="Add Item", command=self.addstuff, width=150
        )
        self.AddButton.grid(row=2, column=1, padx=10, pady=10)

        # Dropdown and Edit Section
        self.EditFrame = customtkinter.CTkFrame(self, corner_radius=10)
        self.EditFrame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        self.EditItemLabel = customtkinter.CTkLabel(self.EditFrame, text="Edit Existing Item", font=("Arial", 18))
        self.EditItemLabel.grid(row=0, column=0, columnspan=2, pady=10)

        self.CurrentDocumentsDropdown = customtkinter.CTkOptionMenu(
            self.EditFrame, values=item_names, width=200
        )
        self.CurrentDocumentsDropdown.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.EditSelectedDropdown = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Name")
        self.EditSelectedDropdown.grid(row=2, column=0, padx=10, pady=5)

        self.DropDownEditButton = customtkinter.CTkButton(
            self.EditFrame, text="Update Name", command=self.update_name, width=150
        )
        self.DropDownEditButton.grid(row=2, column=1, padx=10, pady=10)

        # Logs and Additional Options Section
        self.OptionsFrame = customtkinter.CTkFrame(self, corner_radius=10)
        self.OptionsFrame.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        self.LogsButton = customtkinter.CTkButton(
            self.OptionsFrame, text="View Logs", command=self.logs, width=150
        )
        self.LogsButton.grid(row=0, column=0, padx=10, pady=10)

        self.EditButton = customtkinter.CTkButton(
            self.OptionsFrame, text="Edit Options", command=self.edit, width=150
        )
        self.EditButton.grid(row=0, column=1, padx=10, pady=10)

    def edit(self):
        print("whatever")

    def logs(self):
        print("whatever2")

    def addstuff(self):
        id = self.AddIdBox.get().strip()
        name = self.AddNameBox.get().strip()
        amount = self.AddAmountBox.get().strip()

        if id and name and amount:
            try:
                doc1 = {"_id": int(id), "Item": name, "Amount": int(amount)}
                collection.insert_one(doc1)
                print("did it")
            except Exception as e:
                print(f"Error adding item: {e}")
        else:
            print("Put Everythin in")

    def update_name(self):
        selected_item = self.CurrentDocumentsDropdown.get()
        new_name = self.EditSelectedDropdown.get().strip()

        if selected_item and new_name:
            try:
                result = collection.update_one({"Item": selected_item}, {"$set": {"Item": new_name}})
                if result.modified_count > 0:
                    print(f"Updated '{selected_item}' to '{new_name}'")
                    self.refresh_dropdown()
                else:
                    print("No item was updated.")
            except Exception as e:
                print(f"Error updating item: {e}")
        else:
            print("Please select an item and enter a new name.")

    def refresh_dropdown(self):
        global item_names
        item_names = [doc["Item"] for doc in collection.find()]
        self.CurrentDocumentsDropdown.configure(values=item_names)

app = App()
app.mainloop()
