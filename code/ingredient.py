from functions import *
import mysql.connector

# Allows for dynamic creation of an object from the database
class Ingredient:
    def __init__(self, ingredient_name: str, connection):
        self.connection = connection
        self.ingredient_name = ingredient_name
        
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT * FROM ingredients WHERE ingredient_name = %s",
                (ingredient_name,)
            )
            
            db_item = cursor.fetchone()

            self.item_id: int = db_item[0]
            self.type_id: int = 1
            self.type: str = db_item[2]

        finally:
            cursor.close()

# This is the function that sends the ingredients in the inventory, to the database shared inventory
def inv_to_database(connection, room_id, inventory):
    cursor = connection.cursor()

    try:
        for (item_name, quantity) in inventory:

            # look up id
            ingredient = Ingredient(item_name, connection)
            item_id = ingredient.item_id

            # Insert the item into the inventory table
            cursor.execute(
                """
                CALL add_inventory_item(1, %s, %s, %s, %s)
                """,
                (item_id, item_name, quantity, room_id)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        
# Puts the player's inventory of ingredients into a printable format for tk.Stringvar   
# name, quantity
def print_ingredients(ingredients: list[tuple[str, int]]) -> str:
    ingredients_str = "Inventory: \n"
    if len(ingredients) > 0:
        for inventory_num in range(len(ingredients)):
            ingredients_str += ingredients[inventory_num][0]
            ingredients_str += ": "
            ingredients_str += str(ingredients[inventory_num][1])
            if inventory_num != (len(ingredients) - 1):
                ingredients_str += "\n "
    else:
        ingredients_str = "Nothing in Inventory"
    return ingredients_str

# Prints ingredients, but compatible with the database
def print_ingredients_full(ingredients: list[tuple[int, int, str, int]]) -> str:
    ingredients_str = "Inventory: \n"
    if len(ingredients) > 0:
        for inventory_num in range(len(ingredients)):
            ingredients_str += ingredients[inventory_num][2]
            ingredients_str += ": "
            ingredients_str += str(ingredients[inventory_num][3])
            if inventory_num != (len(ingredients) - 1):
                ingredients_str += "\n "
    else:
        ingredients_str = "Nothing in Inventory"
    return ingredients_str

# Drops half of your inventory and returns a concatenated string of all non-dropped items
def drop_random_ingredients(ingredients: list[tuple[str, int]]) -> list[tuple[str, int]]:
    #Pythonic way of summing all the quantities
    #Sums all items from their quantities
    total_items: int = sum(x[1] for x in ingredients)
    kept_ingredients: list[tuple[str, int]] = []
        
    # Drops half of your inventory
    for drop_num in range(total_items // 2):
        # Add ingredient to your kept inventory
        node_ingredient = sample_item(ingredients)
        # Protects from weird edge cases
        if node_ingredient is not None:
            # Check whether the player already has this item
            item_found = False

            for i, (inventory_name, quantity) in enumerate(kept_ingredients):
                if inventory_name == node_ingredient:
                    kept_ingredients[i] = (inventory_name, quantity + 1)
                    item_found = True
                    break

            # Add a new item if it isn't already in the inventory
            if not item_found:
                kept_ingredients.append((node_ingredient, 1))
        
        # Removes ingredient from old inventory
        if len(ingredients) > 1:
            for i in range(len(ingredients) - 1):
                if ingredients[i][0] == node_ingredient:
                    item_quantity = ingredients[i][1]
                    ingredients[i] = (node_ingredient, item_quantity-1)
                    # Pops ingredients that have 0 quantity
                    if ingredients[i][1] == 0:
                        ingredients.pop(i)
        else: 
            ingredients = []        
        
    # Returns the concatenated string of all remaining items
    return kept_ingredients

def harvest_item(ingredients_drop_list: list[tuple[str, int]], inventory: list[tuple[str, int]]) -> str:
    node_ingredient: str = sample_item(ingredients_drop_list)
    # Protects from weird edge cases
    if node_ingredient is not None:
        # Check whether the player already has this item
        item_found = False

        for i, (inventory_name, quantity) in enumerate(inventory):
            if inventory_name == node_ingredient:
                inventory[i] = (inventory_name, quantity + 1)
                item_found = True
                break

        # Add a new item if it isn't already in the inventory
        if not item_found:
            inventory.append((node_ingredient, 1))
    return node_ingredient
        
def get_ingredient_name_from_id(connection, item_id) -> str:
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT ingredient_name FROM ingredients WHERE ingredient_id = %s",
            (item_id, )
        )
        result = cursor.fetchone()
        return result[0]
    finally:
        cursor.close()
        
# Returns the name of every ingredient in the database
def get_ingredient_names(connection) -> list[str]:
    cursor = connection.cursor()
    ingredients_names_list: list[str] = []
    try:
        cursor.execute(
            "SELECT ingredient_name FROM ingredients"
        )
        ingredients_tuples = cursor.fetchall()
        for ingredient in ingredients_tuples:
            ingredients_names_list.append(ingredient[0])
        
        return ingredients_names_list
    finally:
        cursor.close()