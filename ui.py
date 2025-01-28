import customtkinter
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = cluster["Inventory"]
collection = db["Inventory"]
item_names = [doc["Item"] for doc in collection.find()]

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.title('Inventory taking')
        self.geometry("800x600")
        #root.attributes ('-fullscreen', True) #not working

        self.TitleLabel = customtkinter.CTkLabel(self,
                                            text="Medical Inventory",
                                            text_color="White",
                                            font=("Arial", 20)



                                            )
        self.TitleLabel.grid(row=1, column=2)


        self.LogsButton = customtkinter.CTkButton(self,
                                     text="Logs",
                                     command=self.logs,
                                     width=300,
                                     height=100,
                                     text_color="White",
                                     )
        self.LogsButton.grid(row=2, column=3, padx=20, pady=20)

        self.EditButton = customtkinter.CTkButton(self,
                                      text="Edit",
                                      command=self.edit,
                                      width=300,
                                      height=100,
                                      text_color="White",
                                      )
        self.EditButton.grid(row=2, column=1, padx=20, pady=20)

        self.AddIdBox = customtkinter.CTkTextbox(master=self,
                                                 width=100,
                                                 height=100,
                                                 corner_radius=0)
        self.AddIdBox.grid(row=3, column=2)
        self.AddIdBox.insert("0.0", "Put id you want here" * 1)

        self.AddNameBox = customtkinter.CTkTextbox(master=self,
                                                    width=100,
                                                    height=100,
                                                    corner_radius=0)
        self.AddNameBox.grid(row=3, column=3)
        self.AddNameBox.insert("0.0", "Put name you want here" * 1)

        self.AddAmountBox = customtkinter.CTkTextbox(master=self,
                                                    width=100,
                                                    height=100,
                                                    corner_radius=0)
        self.AddAmountBox.grid(row=3, column=4)
        self.AddAmountBox.insert("0.0", "Put amount you want here" * 1)

        self.AddButton = customtkinter.CTkButton(self,
                                                 text="Add",
                                                 command=self.addstuff,
                                                 width=100,
                                                 height=100,
                                                 text_color="White"
                                                 )
        self.AddButton.grid(row=3, column=5)

        self.CurrentDocumentsDropdown = customtkinter.CTkOptionMenu(self,
                                                                    values=item_names,
                                                                    width=200,
                                                                    height=30
                                                                    )
        self.CurrentDocumentsDropdown.grid(row=4, column=2, padx=20, pady=20)

    def edit(self):
        print('whatever')

    def logs(self):
        print('whatever2')

    def addstuff(self):
        id = self.AddIdBox.get("1.0", "end").strip()
        name = self.AddNameBox.get("1.0", "end").strip()
        amount = self.AddAmountBox.get("1.0", "end").strip()

        doc1 = {"_id": int(id), "Item": name,
                "Amount": int(amount)}  # use this to put new docs into DB
        collection.insert_one(doc1)



app = App()
app.mainloop()