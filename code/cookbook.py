import json

# Allows for dynamic creation of an object from JSON from just its name
class Cookbook:
    def __init__(self, cookbook_name: str):
        fileObject = open("./assets/JSON/cookbooks.json", "r")
        fileData = json.load(fileObject)[cookbook_name]
        
        self.name = fileData["name"]
        self.area = fileData["area"]
        self.price = fileData["price"]
        self.item_id = fileData["item_id"]
        self.type_id = 4