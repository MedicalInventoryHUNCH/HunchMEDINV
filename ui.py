import customtkinter
import pymongo
from pymongo import MongoClient
from PIL import Image

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
        self.geometry("800x700")

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

        self.ChangeNameButton = customtkinter.CTkButton(
            self.EditFrame, text="Update Name", command=self.update_name, width=150
        )
        self.ChangeNameButton.grid(row=2, column=1, padx=10, pady=10)

        # Change Amount
        self.EditSelectedAmount = customtkinter.CTkEntry(self.EditFrame, placeholder_text="Enter New Amount")
        self.EditSelectedAmount.grid(row=3, column=0, padx=10, pady=5)

        self.ChangeAmountButton = customtkinter.CTkButton(
            self.EditFrame, text="Update Amount", command=self.update_amount, width=150
        )
        self.ChangeAmountButton.grid(row=3, column=1, padx=10, pady=10)

        self.James = customtkinter.CTkImage(dark_image=Image.open("pictures/face7.jpg"), size=(1000,250))
        self.PicOfJames = customtkinter.CTkLabel(self, image=self.James, text="")

        self.PicOfJames.grid(row=1, column=2, padx=10, pady=10)

    def addstuff(self):
        id = self.AddIdBox.get().strip()
        name = self.AddNameBox.get().strip()
        amount = self.AddAmountBox.get().strip()

        if id and name and amount:
            try:
                doc1 = {"_id": int(id), "Item": name, "Amount": int(amount)}
                collection.insert_one(doc1)
                print("Item added successfully!")
                self.refresh_dropdown()
            except Exception as e:
                print(f"Error adding item: {e}")
        else:
            print("Please fill all fields.")

    def update_name(self):
        selected_item = self.CurrentDocumentsDropdown.get()
        new_name = self.EditSelectedName.get().strip()

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

    def update_amount(self):
        selected_item = self.CurrentDocumentsDropdown.get()
        new_amount = self.EditSelectedAmount.get().strip()

        if selected_item and new_amount:
            try:
                result = collection.update_one({"Item": selected_item}, {"$set": {"Amount": int(new_amount)}})
                if result.modified_count > 0:
                    print(f"Updated Amount for '{selected_item}' to '{new_amount}'")
                else:
                    print("No item was updated.")
            except Exception as e:
                print(f"Error updating Amount: {e}")
        else:
            print("Please select an item and enter a new amount.")

    def refresh_dropdown(self):
        global item_names
        item_names = [doc["Item"] for doc in collection.find()]
        self.CurrentDocumentsDropdown.configure(values=item_names)

app = App()
app.mainloop()
