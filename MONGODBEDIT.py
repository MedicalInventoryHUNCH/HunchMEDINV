import ndef
import nfc
from ndef import TextRecord
import pymongo
from pymongo import MongoClient

choice = input("1 for new 2 for edit ")

cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["astro"]
while True:

     if choice == "1":
        id1 = input("input id number: ")
        name = input("name of astro: ")
        amount = input("input amount: ")
        amount2 = input("input amount: ")
        amount3 = input("input amount: ")
        amount4 = input("input amount: ")
        amount5 = input("input amount: ")
        amount6 = input("input amount: ")


        doc1 = {"_id":int(id1), "Item":name,
                "Amount_1":int(amount), "Amount_2":int(amount2), "Amount_3":int(amount3), "Amount_4":int(amount4),"Amount_5":int(amount5),"Amount_6":int(amount6),
                } #use this to put new docs into DB
        collection.insert_one(doc1)
        break

     if choice == "2":
            # if sigma then Skibidi, else Beta
        id2 = input("input id number: ")
        num2 = input("enter amount: ")
        collection.update_many({"_id": int(id2)}, {"$set": {"Amount": int(num2)}})
        break



print("Updated Successfully :D")
