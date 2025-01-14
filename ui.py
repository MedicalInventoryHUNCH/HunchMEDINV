import customtkinter
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
root = customtkinter.CTk()
root.title('Inventory taking bleh bleh bleh')
root.geometry("800x600")

def Edit():
    print("work")

EditButton = customtkinter.CTkButton(root,
                                      text="Edit",
                                      command=Edit(),
                                      width=298,
                                      height=100,
                                      text_color="White",
                                      )



EditButton.grid(row=0, column=0)
EditButton.pack(pady=180)

root.mainloop()
