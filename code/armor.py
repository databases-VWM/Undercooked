import json

# Allows for dynamic creation of an object from JSON from just its name
class Armor:
    def __init__(self, armor_name: str):
        fileObject = open("./assets/JSON/armors.json", "r")
        fileData = json.load(fileObject)[armor_name]

        # Imported Properties
        self.name: str = fileData["name"]
        self.type: int = fileData["type"]
        self.defense: int = fileData["defense"]
        self.block_dice: list[list[int]] = fileData["block_dice"]
        self.dodge_dice: list[list[int]] = fileData["dodge_dice"]
        self.item_id: int = fileData["item_id"]
        self.type_id: int = 3