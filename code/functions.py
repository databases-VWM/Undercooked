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



# Temporary function for reference
# def build_object_from_db(connection, table_name, id):
#     cursor = connection.cursor()

#     cursor.execute(
#         "SELECT * FROM %s WHERE id = %s",
#         (table_name, id)
#     )
#     result = cursor.fetchall()
#     for (column1, column2, column3, column4) in result:
#         self.column1 = column1
#         self.column2, = column2
#         self.column3 = column3
#         self.column4 = column4

