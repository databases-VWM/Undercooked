import json

# Allows for dynamic creation of an object from JSON from just its name
class Enemy:
    def __init__(self, enemy_name: str):
        fileObject = open("./assets/JSON/enemies.json", "r")
        fileData = json.load(fileObject)[enemy_name]

        # Imported Properties
        self.name: str = fileData["name"]
        self.health: int = fileData["health"]
        self.defense: int = fileData["defense"]
        self.attack_dice: list[list[int]] = fileData["attack_dice"]
        self.block_dice: list[list[int]] = fileData["block_dice"]
        self.dodge_dice: list[list[int]] = fileData["dodge_dice"]
        self.is_boss: bool = fileData["is_boss"]
