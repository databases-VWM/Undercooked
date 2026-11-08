import random
import json

# This is a function that just allows for setting values within tkinter commands
def set_value_from_button(buttonValue, newValue):
    newValue = buttonValue

def sample_item(items: list[tuple[str, int]]) -> str:
    """
    Returns a random item from the given list, where each element is
    in the form (name, weight). Sampling weighted by item weight

    Usage:
    enemy = sample_item(enemies)
    """
    return random.choices(items, weights=[x[1] for x in items], k=1)[0][0]

def get_item_names(fname: str) -> list[str]:
    """
    Returns a list of all item names in a file

    Usage:
    area_names = get_item_names('area.json')
    """
    with open("../assets/JSON/" + fname, "r") as file_object:
        return list(json.load(file_object).keys())

def get_attribute_from_names(fname: str, item_names: list[str], attr: str) -> list:
    """
    Returns a list containing the requested attribute for all given items names

    Usage:
    armor_ids = get_attribute_from_names('armor.json', armor_names, 'item_id')
    """
    with open("../assets/JSON" + fname, "r") as file_object:
        file_data = json.load(file_object)
        return [x[attr] for x in file_data.values() if x['name'] in item_names]
