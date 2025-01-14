import ndef
import nfc
from ndef import TextRecord
import pymongo
from pymongo import MongoClient

choice = input("1 for new 2 for edit")

cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]
while True:

     if choice == "1":
        id = input("input id number:")
        name = input("name of medication:")
        amount = input("input amount:")

        doc1 = {"_id":int(id), "Item":name, "Amount":int(amount)} #use this to put new docs into DB
        collection.insert_one(doc1)
        break

     if choice == "2":
            # if sigma then Skibidi, else Beta
