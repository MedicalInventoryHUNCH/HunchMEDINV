import customtkinter
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = cluster["Inventory"]
collection = db["Inventory"]

#doc1 = {"_id":5, "Item":"Morphine", "Amount":56} #use this to put new docs into DB

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.title('Inventory taking bleh bleh bleh')
        self.geometry("800x600")
        #root.attributes ('-fullscreen', True) #not working

        self.LogsButton = customtkinter.CTkButton(self,
                                     text="Logs",
                                     command=self.logs,
                                     width=300,
                                     height=100,
                                     text_color="White",
                                     )
        self.LogsButton.grid(row=1, column=0, padx=20, pady=20)

        self.EditButton = customtkinter.CTkButton(self,
                                      text="Edit",
                                      command=self.edit,
                                      width=300,
                                      height=100,
                                      text_color="White",
                                      )
        self.EditButton.grid(row=0, column=0, padx=20, pady=20)

    def edit(self):
        print('whatever')

    def logs(self):
        print('whatever2')



app = App()
app.mainloop()
