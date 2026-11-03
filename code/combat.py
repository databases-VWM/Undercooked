"""
This is just a json loading test, formatted in a way that we may be able to turn it into the actual combat logic.
"""

import json
from pathlib import Path

JSON_FOLDER = Path(__file__).parent.parent / "assets" / "JSON"

def load_json(filename):
    file_path = JSON_FOLDER / filename

    with open(file_path, "r") as file:
        return json.load(file)

def load_game_data():
    enemies = load_json("enemies.json")
    weapons = load_json("weapons.json")
    armors = load_json("armors.json")

    return enemies, weapons, armors

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100 # Temporary value, balance later
        self.weapon = None
        self.armor = None

    def equip_weapon(self, weapon):
        self.weapon = weapon
        print("Equipped:", weapon["name"])

    def unequip_weapon(self):
        self.weapon = None
        print("Unequipped weapon")

    def equip_armor(self, armor):
        self.armor = armor
        print("Equipped:", armor["name"])
    
    def unequip_armor(self):
        self.armor = None
        print("Unequipped Armor")

    

    def show_equipment(self):
        print("\n--- Current Equipment ---")

        if self.weapon:
            print("Weapon:", self.weapon["name"])
            print("Attack Dice:", self.weapon["attack_dice"])
            print("Modifier:", self.weapon["modifier"])
        else:
            print("Weapon: None")

        if self.armor:
            print("Armor:", self.armor["name"])
            print("Defense:", self.armor["defense"])
            print("Block Dice:", self.armor["block_dice"])
            print("Dodge Dice:", self.armor["dodge_dice"])
        else:
            print("Armor: None")

# Displaying enemies
def show_enemies(enemies):
    print("\n--- Enemies ---")

    for name, enemy in enemies.items():
        print(f"{name} | HP: {enemy['health']} | Defense: {enemy['defense']}")

# Display weapons
def show_weapons(weapons):
    print("\n--- Available Weapons ---")

    for name, weapon in weapons.items():
        print(f"{name} | Modifier: {weapon['modifier']}")


# Display armor
def show_armors(armors):
    print("\n--- Available Armor ---")

    for name, armor in armors.items():
        print(f"{name} | Defense: {armor['defense']}")


# Select and equip a weapon/armor
def select_weapon(player, weapons):
    show_weapons(weapons)

    choice = input("\nEnter weapon name: ")

    if choice in weapons:
        player.equip_weapon(weapons[choice])
    else:
        print("Invalid weapon")

def select_armor(player, armors):
    show_armors(armors)

    choice = input("\nEnter armor name: ")

    if choice in armors:
        player.equip_armor(armors[choice])
    else:
        print("Invalid armor selection.")

def select_enemy(enemies):
    show_enemies(enemies)

    choice = input("\nEnter enemy name: ")

    if choice in enemies:
        enemy = enemies[choice]

        print("\n--- Enemy Selected ---")
        print("Name:", enemy["name"])
        print("Health:", enemy["health"])
        print("Defense:", enemy["defense"])
        print("Attack Dice:", enemy["attack_dice"])

        return enemy

    print("Invalid enemy selection.")
    return None


def main():
    try:
        enemies, weapons, armors = load_game_data()
    except FileNotFoundError as error:
        print("Could not find JSON file:", error)
        return
    except json.JSONDecodeError as error:
        print("Invalid JSON file:", error)
        return

    player = Player("Test Player")

    while True:
        print("\n========== RPG COMBAT TEST ==========")
        print("1. Select Enemy")
        print("2. Equip Weapon")
        print("3. Equip Armor")
        print("4. Show Equipment")
        print("5. Unequip Equipment")
        print("6. Exit")

        choice = input("\nSelect an option: ")

        if choice == "1":
            select_enemy(enemies)

        elif choice == "2":
            select_weapon(player, weapons)

        elif choice == "3":
            select_armor(player, armors)

        elif choice == "4":
            player.show_equipment()
        
        elif choice == "5":
            choice = input("Unequip weapon or armor? (1/2)")
            if choice == "1":
                player.unequip_weapon(player)
            elif choice == "2":
                player.unequip_armor(player)
            else:
                print("Invalid selection")

        elif choice == "6":
            print("Exiting combat test.")
            break

        else:
            print("Invalid selection.")


# Run program
if __name__ == "__main__":
    main()