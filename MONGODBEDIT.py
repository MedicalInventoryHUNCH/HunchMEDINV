import ndef
import nfc
from ndef import TextRecord
import pymongo
from pymongo import MongoClient



cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]

doc1 = {"_id":4, "Item":"Pepto-Bismol", "Amount":300}

collection.insert_one(doc1)