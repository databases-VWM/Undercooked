import random
import mysql.connector

from functions import *
from entity import *


#Attempting to write a function that can build areas using the database
class Area:
    def __init__(self, area_name: str, connection):
        self.connection = connection
        cursor = self.connection.cursor()

        try:
            # Retrieve basic area information
            cursor.execute(
                """
                SELECT area_name, area_power
                FROM areas
                WHERE area_name = %s
                """,
                (area_name,)
            )

            result = cursor.fetchone() # fetch one cause there should only be one with that name

            if result is None:
                raise ValueError(f"Area '{area_name}' does not exist.")

            self.name = result[0]
            self.recommended_power = result[1]

            # Retrieve enemies and their weights
            cursor.execute(
                """
                SELECT enemy_name, enemy_weight
                FROM area_enemies
                WHERE area_name = %s
                """,
                (area_name,)
            )

            self.enemies_list = cursor.fetchall()

            # Retrieve ingredients and their weights
            cursor.execute(
                """
                SELECT ingredients.ingredient_name,
                    ingredients.ingredient_type,
                    area_ingredients.ingredient_weight
                FROM area_ingredients
                JOIN ingredients
                    ON area_ingredients.ingredient_id = ingredients.ingredient_id
                WHERE area_ingredients.area_name = %s
                """,
                (area_name,)
            )

            ingredients = cursor.fetchall()

            # Separate ingredients by type
            self.fishing_list = []
            self.flora_list = []
            self.fauna_list = []

            for ingredient_name, ingredient_type, weight in ingredients:
                if ingredient_type == "fish":
                    self.fishing_list.append((ingredient_name, weight))

                elif ingredient_type == "plant":
                    self.flora_list.append((ingredient_name, weight))

                elif ingredient_type == "meat":
                    self.fauna_list.append((ingredient_name, weight))

        finally:
            cursor.close()

        self.chosen_list = []

        # TODO Map unlock, idk how you want to implement this
        # self.map_unlock = ""

        # Flags for integration with game.py
        self.current_node: int = 0
        self.progress: bool = True
        self.node_type: str = ""
        self.is_enemy: bool = False
        self.is_elite: bool = False
        self.is_boss: bool = False
        self.enemy_name: str = ""

        # Constants for game balancing
        self.ENEMY_CHANCE: float = 0.50
        self.ELITE_THRESHOLD: int = 100
        


# Allows for dynamic creation of an object from JSON from just its name
#Ingredients list arrays and enemies/bosses list arrays are in the format [[item_name, weight], [item_name, weight]]
# class Area:
#     def __init__(self, area_name: str, connection):
#         cursor = connection.cursor()
#         try:
#             cursor.execute(
                
#             )
#         except:
#             pass
                
#         # with open("../assets/JSON/areas.json", "r") as file_object:
#         #     file_data = json.load(file_object)[area_name]

#         #     # Imported Properties
#         #     self.name: str = file_data["name"]
#         #     self.recommended_power = file_data["recommended_power"]
#         #     self.enemies_list: list[tuple[str, int]] = file_data["enemies_list"]
#         #     self.fishing_list: list[tuple[str, int]] = file_data["fishing_list"]
#         #     self.flora_list: list[tuple[str, int]] = file_data["flora_list"]
#         #     self.fauna_list: list[tuple[str, int]] = file_data["fauna_list"]
#         #     self.chosen_list = []
#         #     self.map_unlock: str = file_data["map_unlock"]


#         #     # Flags for integration with game.py
#         #     self.current_node: int = 0
#         #     self.progress: bool = True
#         #     self.node_type: str = ""
#         #     self.is_enemy: bool = False
#         #     self.is_elite: bool = False
#         #     self.is_boss: bool = False
#         #     self.enemy_name: str = ""

#         #     # Constants for game balancing
#         #     self.ENEMY_CHANCE: float = 0.30
#         #     self.ELITE_THRESHOLD: int = 100

    # Handles generation of and setting flags for a standard node
    def generate_node(self) -> None:
        # Resets flags
        self.node_type = " "
        self.is_enemy = False
        self.is_elite = False
        self.is_boss = False

        # Determine node type
        node_categories = [
            ("fishing", len(self.fishing_list)),
            ("flora", len(self.flora_list)),
            ("fauna", len(self.fauna_list))
        ]

        # Remove categories with no available items
        available_categories = [
            category for category in node_categories if category[1] > 0 # Protects against edge cases
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
            # DETERMINE IF ELITE
            if (random.random() * self.ELITE_THRESHOLD >= self.ELITE_THRESHOLD - self.current_node):
                self.is_elite = True
            else:
                self.is_elite = False
        else:
            self.is_enemy = False
        


        # Generate actual enemy
        self.enemy_name = sample_item(self.enemies_list)

#Sets up string for the ingredient forecast for a given area
def setup_ingredients_forecast(area_name: str, connection) -> str:
    try:
        # Temporarily loads up a given area
        new_area = Area(area_name, connection)
        total_ingredients_array: list[tuple[str, int]] = []
        ingredients_forecast_str = f"Recommended Power: {new_area.recommended_power}\nIngredients Forecast:\n"
        
        for ingredient_tuple in new_area.flora_list:
            total_ingredients_array.append(ingredient_tuple)
        for ingredient_tuple in new_area.fauna_list:
            total_ingredients_array.append(ingredient_tuple)
        for ingredient_tuple in new_area.fishing_list:
            total_ingredients_array.append(ingredient_tuple)
        # Sort list by weights
        total_ingredients_array.sort(key= lambda x: x[1])
        for ingredient_num in range(30):
            #Tries to add new ingredients to the forecast. If they don't exist, pass until loop ends
            try:
                ingredients_forecast_str += total_ingredients_array[ingredient_num][0]
                ingredients_forecast_str += "\n"
            except IndexError:
                pass
        if len(total_ingredients_array) > 30:
            ingredients_forecast_str += "... Plus more"
    except ValueError:
        ingredients_forecast_str = "No ingredients to display"
    return ingredients_forecast_str

# Database function to return all area names
def get_area_names(connection, room_id) -> list[str]:
    cursor = connection.cursor()
    areas_list: list[str] = []
    try:
        cursor.execute(
            "SELECT * FROM cookbooks NATURAL JOIN unlocked_cookbooks NATURAL RIGHT JOIN areas WHERE room_id = %s OR room_id is NULL",
            (room_id, )
        )
        area_tuples = cursor.fetchall()
        for row in area_tuples:
            areas_list.append(row[0])
        return areas_list
    finally:
        cursor.close()
        
    
    
    