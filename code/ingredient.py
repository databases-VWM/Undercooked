import json

# Allows for dynamic creation of an object from JSON from just its name
class Ingredient:
    def __init__(self, ingredient_name: str):
        fileObject = open("./assets/JSON/enemies.json", "r")
        fileData = json.load(fileObject)[ingredient_name]

        # Imported Properties
        self.name: str = fileData["name"]
        self.type: str = fileData["type"]
        self.rare_ingredient: bool = fileData["rare_ingredient"]
        self.legendary_ingredient: bool = fileData["legendary_ingredient"]
        self.score: int = fileData["score"]
        self.item_id: int = fileData["item_id"]
        self.type_id: int = 1
