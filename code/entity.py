import json

# Allows for dynamic creation of an object from JSON from just its name
class Entity:
    def __init__(self, entity_name: str, user_ID: int = 0):
        if entity_name != "Player":
            fileObject = open("../assets/JSON/enemies.json", "r") # NOTE: I HAD TO CHANGE PATH TO .. TO TEST COMBAT.py
            fileData = json.load(fileObject)[entity_name]

            # Imported Properties
            self.name: str = fileData["name"]
            self.weapon: str = ""
            self.armor: str = ""
            self.health: int = fileData["health"]
            self.max_health = self.health
            self.defense: int = fileData["defense"]
            self.attack_dice: list[list[int]] = fileData["attack_dice"]
            self.block_dice: list[list[int]] = fileData["block_dice"]
            self.dodge_dice: list[list[int]] = fileData["dodge_dice"]
            self.description: str = fileData["description"]
            self.is_boss: bool = fileData["is_boss"]
        else:
            # Testing defaults
            self.name: str = "Me"
            self.weapon: str = "These hands"
            self.armor: str = "Traveler's Garbs"
            self.health: int = 100
            self.max_health: int = self.health
            self.defense: int = 10
            self.attack_dice: list[list[int]] = [[2,5], [10,10]] # Default for combat demo testing
            self.block_dice: list[list[int]] = [[5,2]]
            self.dodge_dice: list[list[int]] = [[3,3]]
            self.description: str = "A mighty chef"
            self.is_boss: bool = False

            self.get_player_data_from_database()

    # This functions fills in all the player data from the database
    def get_player_data_from_database(self):
        pass
        
# Takes a category of dice and an entity and transforms that array into an appended string for display
# Type = "attack", "guard", "dodge"
def transform_dice_to_str(entity: Entity, type: str) -> str:
    dice_list: list[list[int]]
    die_str = ""
    if type.lower() == "attack":
        dice_list = entity.attack_dice
    elif type.lower() == "guard":
        dice_list = entity.block_dice
    elif type.lower() == "dodge":
        dice_list = entity.dodge_dice
    
    # Each die rolled
    for die_num in range(len(dice_list)):
        die_str += str(dice_list[die_num][0])
        die_str += "d"
        die_str += str(dice_list[die_num][1])
        if die_num != (len(dice_list) - 1):
            die_str += ", "
    
    return die_str
        
    
#Function that puts stats into an array to be outputted by another function
def output_entity_stats(entity: Entity, extended: bool = False) -> list[str]:
    entity_array: list[str] = []
    entity_array.append(f"{entity.name}'s stats:")
    entity_array.append(f"{entity.health} / {entity.max_health} Health")
    if extended == True:
        attack_die_str = transform_dice_to_str(entity, "attack")
        guard_die_str = transform_dice_to_str(entity, "guard")
        dodge_die_str = transform_dice_to_str(entity, "dodge")
        entity_array.append(f"Weapon: {entity.weapon}")
        entity_array.append(f"Armor: {entity.armor}")
        entity_array.append(f"Defense: {entity.defense}")
        entity_array.append(f"Damage: {attack_die_str}")
        entity_array.append(f"Guard: {guard_die_str}")
        entity_array.append(f"Dodge: {dodge_die_str}")
    entity_array.append(f"\"{entity.description}\"")
    return entity_array
        
