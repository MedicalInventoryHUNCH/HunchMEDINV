
import ndef
import nfc
from ndef import TextRecord
import pymongo
from pymongo import MongoClient


clf = nfc.ContactlessFrontend('usb')

cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection = db["Inventory"]

def idnumber():
    if "NFCNASAMED" in str(tag_data):
        print("scanned" + str(tag_data))
        meds = str(tag_data)
        splitmeds = meds.split('%')
        print(int(splitmeds[2]))
        intmeds = int(splitmeds[2])
        return intmeds
    else:
        print("med unknown tag")

while True:

    tag = clf.connect(rdwr={'on-connect': lambda tag: False})
    tag_data = tag.ndef.records

    idnumber()

    collection.update_many({"_id":idnumber()}, {"$inc":{"Amount":-1}})
    break


