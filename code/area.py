import json

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
