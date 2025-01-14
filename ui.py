import customtkinter
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = cluster["Inventory"]
collection = db["Inventory"]

#doc1 = {"_id":5, "Item":"Morphine", "Amount":56} #use this to put new docs into DB

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
root = customtkinter.CTk()
root.title('Inventory taking bleh bleh bleh')
root.geometry("800x600")

def Edit():
    print('whatever')
    return

def Logs():
    print('whatever2')
    return

LogsButton = customtkinter.CTkButton(root,
                                     text="Logs",
                                     command=Logs(),
                                     width=300,
                                     height=100,
                                     text_color="White",
                                     )

EditButton = customtkinter.CTkButton(root,
                                      text="Edit",
                                      command=Edit(),
                                      width=300,
                                      height=100,
                                      text_color="White",
                                      )





EditButton.grid(row=0, column=0, padx=20, pady=20)
LogsButton.grid(row=1,column=0, padx=20, pady=20)

root.mainloop()
