import json

# Allows for dynamic creation of an object from JSON from just its name
class Weapon:
    def __init__(self, weapon_name: str):
        fileObject = open("../assets/JSON/weapons.json", "r")
        fileData = json.load(fileObject)[weapon_name]

        # Imported Properties
        self.name: str = fileData["name"]
        self.attack_dice: list[list[int]] = fileData["attack_dice"]
        self.modifier: int = fileData["modifier"]
        self.item_id: int = fileData["item_id"]
        self.price: int = fileData["price"]
        self.type_id: int = 2

    def display(self) -> :
        weapon_blurb: str = f"{self.name}:\nAttack Roll: {transform_dice_to_str(self.attack_dice)}\n Average Damage: {dice_avg(displayed_weapon.attack_dice)}\nAttack Modifier: {displayed_weapon.modifier}\nPrice: {displayed_weapon.price}"
        return 