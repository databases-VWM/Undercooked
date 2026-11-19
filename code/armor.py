import json
from entity import *

# Allows for dynamic creation of an object from JSON from just its name
class Armor:
    def __init__(self, armor_name: str):
        fileObject = open("../assets/JSON/armors.json", "r")
        fileData = json.load(fileObject)[armor_name]

        # Imported Properties
        self.name: str = fileData["name"]
        self.type: int = fileData["type"]
        self.defense: int = fileData["defense"]
        self.block_dice: list[list[int]] = fileData["block_dice"]
        self.dodge_dice: list[list[int]] = fileData["dodge_dice"]
        self.price: int = fileData["price"]
        self.item_id: int = fileData["item_id"]
        self.type_id: int = 3
        
    # Returns a string that outputs the stats of a armor
    def display(self) -> str:
        armor_blurb: str = f"{self.name}:\n Type: {self.type}\nDefense: {self.defense}\n Block Dice: {transform_dice_to_str(self.block_dice)}\nDodge Dice: {transform_dice_to_str(self.dodge_dice)}\nPrice: {self.price}"
        return armor_blurb