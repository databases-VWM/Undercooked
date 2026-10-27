import json

# Allows for dynamic creation of an object from JSON from just its name
#Ingredients list arrays and enemies/bosses list arrays are in the format [[item_name, weight], [item_name, weight]]
class Area:
    def __init__(self, area_name: str):
        fileObject = open("./assets/JSON/areas.json", "r")
        fileData = json.load(fileObject)[area_name]

        # Imported Properties
        self.name: str = fileData["name"]
        self.recommend_power = fileData["recommended_power"]
        self.bosses_list: list[tuple[str, int]] = fileData["bosses_list"]
        self.enemies_list: list[tuple[str, int]] = fileData["enemies_list"]
        self.fishing_list: list[tuple[str, int]] = fileData["fishing_list"]
        self.flora_list: list[tuple[str, int]] = fileData["flora_list"]
        self.fauna_list: list[tuple[str, int]] = fileData["fauna_list"]
        self.map_unlock: str = fileData["map_unlock"]
