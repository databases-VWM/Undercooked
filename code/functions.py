import random
import json

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
    Appends .json

    Usage:
    area_names = get_item_names('areas')
    """
    with open("../assets/JSON/" + fname + ".json", "r") as file_object:
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

# Database editor functions:

# Submits a new ingredient entry into the appropriate tables
def submit_editor_ingredient(connection, ingredient_name: str, ingredient_type: str, area_name: str, ingredient_weight: int):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT max(ingredient_id) FROM ingredients"
        )
        max_id = cursor.fetchone()
        
        cursor.execute(
            "INSERT INTO ingredients VALUES(%s, %s, %s)",
            (max_id + 1, ingredient_name, ingredient_type)
        )
        
        cursor.execute(
            "INSERT INTO area_ingredients VALUES(%s, %s, %s)",
            (area_name, max_id + 1, ingredient_weight)
        )
        
        connection.commit()
        
    except:
        connection.rollback()
    finally:
        cursor.close()