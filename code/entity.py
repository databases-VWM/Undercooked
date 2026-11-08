import json

# Allows for dynamic creation of an object from JSON from just its name
class Entity:
    def __init__(self, entity_name: str, user_ID: int = 0):
        if entity_name != "Player":
            fileObject = open("./assets/JSON/enemies.json", "r")
            fileData = json.load(fileObject)[entity_name]

            # Imported Properties
            self.name: str = fileData["name"]
            self.health: int = fileData["health"]
            self.defense: int = fileData["defense"]
            self.attack_dice: list[list[int]] = fileData["attack_dice"]
            self.block_dice: list[list[int]] = fileData["block_dice"]
            self.dodge_dice: list[list[int]] = fileData["dodge_dice"]
            self.is_boss: bool = fileData["is_boss"]
            #This is just here for the sake of consistency
            self.checkpoints = []
        else:
            self.get_player_data_from_database()

    # This functions fills in all the player data from the database
    def get_player_data_from_database(self):
        # List of tuples ontaining this player's checkpoints. Tuple of area name, checkpoint node
        self.checkpoints: list[tuple[str, int]] = []
        

        
