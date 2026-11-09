import json
import random

from functions import sample_item
from entity import Entity

# Allows for dynamic creation of an object from JSON from just its name
#Ingredients list arrays and enemies/bosses list arrays are in the format [[item_name, weight], [item_name, weight]]
class Area:
    def __init__(self, area_name: str):
        with open("./assets/JSON/areas.json", "r") as file_object:
            file_data = json.load(file_object)[area_name]

            # Imported Properties
            self.name: str = file_data["name"]
            self.recommend_power = file_data["recommended_power"]
            self.bosses_list: list[tuple[str, int]] = file_data["bosses_list"]
            self.enemies_list: list[tuple[str, int]] = file_data["enemies_list"]
            self.fishing_list: list[tuple[str, int]] = file_data["fishing_list"]
            self.flora_list: list[tuple[str, int]] = file_data["flora_list"]
            self.fauna_list: list[tuple[str, int]] = file_data["fauna_list"]
            self.map_unlock: str = file_data["map_unlock"]
            self.current_node = 1
        

    def start_rpg(self):
        self.current_node = 1
        inventory = []

        print(f"\nStarting RPG in: {self.name}")
        print("=" * 40)

        while True:
            print(f"\nNode {current_node}")
            print("-" * 40)

            # Step 1: Check for campsite/checkpoint nodes
            if self.current_node % 10 == 0:
                print("CHECKPOINT")
                print("CAMPSITE")

            elif self.current_node % 5 == 0:
                print("CAMPSITE")

            else:
                selected_item = None

                # Step 2: Select a node category using Max's weighted function
                node_categories = [
                    ("Fishing", len(self.fishing_list)),
                    ("Flora", len(self.flora_list)),
                    ("Fauna", len(self.fauna_list))
                ]

                # Remove categories with no available items
                available_categories = [
                    category for category in node_categories if category[1] > 0 # Protects against edgecases
                ]

                if not available_categories:
                    print("No resources are available in this area.")

                else:
                    selected_category = sample_item(available_categories)
                    category_name = selected_category[0]

                    print(f"Node Type: {category_name}")

                    # Step 3: Select the actual resource
                    if category_name == "Fishing":
                        category_list = self.fishing_list
                    elif category_name == "Flora":
                        category_list = self.flora_list
                    else:
                        category_list = self.fauna_list

                    selected_item = sample_item(category_list)

                # Step 4: Roll for an enemy encounter
                if len(self.enemies_list) > 0 and random.random() < 0.30:
                    print("\nENEMY ENCOUNTER!!!!!!!!!!")

                    selected_enemy = sample_item(self.enemies_list)
                    enemy_name = selected_enemy[0]

                    enemy = entity(enemy_name)

                    print(f"\nEnemy: {enemy.name}")
                    print(f"Health: {enemy.health}")
                    print(f"Defense: {enemy.defense}")
                    print(f"Attack Dice: {enemy.attack_dice}")
                    print(f"Block Dice: {enemy.block_dice}")
                    print(f"Dodge Dice: {enemy.dodge_dice}")
                    print(f"Boss: {enemy.is_boss}")

                    print("\nFight logic would happen here!")

                else:
                    print("\nNo enemy encountered.")

                # step 5: Award the resource after the encounter
                if selected_item is not None:
                    item_name = selected_item[0]

                    print(f"\nResource Found: {item_name}")

                    # Check whether the player already has this item
                    item_found = False

                    for i, (inventory_name, quantity) in enumerate(inventory):
                        if inventory_name == item_name:
                            inventory[i] = (inventory_name, quantity + 1)
                            item_found = True
                            break

                    # Add a new item if it isn't already in the inventory
                    if not item_found:
                        inventory.append((item_name, 1))

                # Step 6: Display inventory
                print("\nPLAYER INVENTORY")
                print("-" * 40)

                if not inventory:
                    print("Inventory is empty.")

                else:
                    for item_name, quantity in inventory:
                        print(f"{item_name}: {quantity}")

            # Wait for the player to advance or exit
            user_input = input("\nPress Enter to continue, type 'exit' to quit: ")

            if user_input.lower() == "exit":
                print("\nLeaving the area.")
                break

            self.current_node += 1

test_area = Area("Craw's Domain")

test_area.start_rpg()