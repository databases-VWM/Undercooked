import json
import random

from functions import *
from entity import *

# Allows for dynamic creation of an object from JSON from just its name
#Ingredients list arrays and enemies/bosses list arrays are in the format [[item_name, weight], [item_name, weight]]
class Area:
    def __init__(self, area_name: str):
        with open("../assets/JSON/areas.json", "r") as file_object:
            file_data = json.load(file_object)[area_name]

            # Imported Properties
            self.name: str = file_data["name"]
            self.recommend_power = file_data["recommended_power"]
            self.bosses_list: list[tuple[str, int]] = file_data["bosses_list"]
            self.enemies_list: list[tuple[str, int]] = file_data["enemies_list"]
            self.fishing_list: list[tuple[str, int]] = file_data["fishing_list"]
            self.flora_list: list[tuple[str, int]] = file_data["flora_list"]
            self.fauna_list: list[tuple[str, int]] = file_data["fauna_list"]
            self.chosen_list = []
            self.map_unlock: str = file_data["map_unlock"]


            # Flags for integration with game.py
            self.current_node: int = 0
            self.progress: bool = True
            self.node_type: str = ""
            self.is_enemy: bool = False
            self.is_elite: bool = False
            self.enemy_name: str = ""

            # Constants for game balancing
            self.ENEMY_CHANCE: float = 0.30
            self.ELITE_THRESHOLD: int = 100

    # Handles generation of and setting flags for a standard node
    def generate_node(self) -> None:
        # Resets flags
        self.node_type = " "
        self.is_enemy = False
        self.is_elite = False

        # Determine node type
        node_categories = [
            ("fishing", len(self.fishing_list)),
            ("flora", len(self.flora_list)),
            ("fauna", len(self.fauna_list))
        ]

        # Remove categories with no available items
        available_categories = [
            category for category in node_categories if category[1] > 0 # Protects against edgecases
        ]
        if not available_categories:
            print("ERROR: No resources are available in this area.")

        else:
            self.node_type = sample_item(available_categories)

        # Sets "chosen list" to the list that is equal to the chosen node type
        if (self.node_type == "fishing"):
            self.chosen_list = self.fishing_list
        elif (self.node_type == "flora"):
            self.chosen_list = self.flora_list
        elif (self.node_type == "fauna"):
            self.chosen_list = self.fauna_list

        # DETERMINE IF ENEMY
        if len(self.enemies_list) > 0 and random.random() < self.ENEMY_CHANCE:
            self.is_enemy = True
        else:
            self.is_enemy = False
        
        # DETERMINE IF ELITE
        if (random.random() * self.ELITE_THRESHOLD >= self.ELITE_THRESHOLD - self.current_node):
            self.is_elite = True
        else:
            self.is_elite = False

        # Generate actual enemy
        self.enemy_name = sample_item(self.enemies_list)
