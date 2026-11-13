import json

# Allows for dynamic creation of an object from JSON from just its name
class Entity:
    def __init__(self, entity_name: str, user_ID: int = 0):
        if entity_name != "Player":
            fileObject = open("../assets/JSON/enemies.json", "r") # NOTE: I HAD TO CHANGE PATH TO .. TO TEST COMBAT.py
            fileData = json.load(fileObject)[entity_name]

            # Imported Properties
            self.name: str = fileData["name"]
            self.health: int = fileData["health"]
            self.max_health = self.health
            self.defense: int = fileData["defense"]
            self.attack_dice: list[list[int]] = fileData["attack_dice"]
            self.block_dice: list[list[int]] = fileData["block_dice"]
            self.dodge_dice: list[list[int]] = fileData["dodge_dice"]
            self.is_boss: bool = fileData["is_boss"]
        else:
            # Testing defaults
            self.name: str = "Me"
            self.health: int = 100
            self.max_health: int = self.health
            self.health: int = 1000
            self.defense: int = 50
            self.attack_dice: list[list[int]] = [[2,5], [10,10]] # Default for combat demo testing
            self.block_dice: list[list[int]] = [[5,2]]
            self.dodge_dice: list[list[int]] = [[3,3]]
            self.is_boss: bool = False

            self.get_player_data_from_database()

    # This functions fills in all the player data from the database
    def get_player_data_from_database(self):
        pass
        

        
