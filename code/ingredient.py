import json

# Allows for dynamic creation of an object from JSON from just its name
class Ingredient:
    def __init__(self, ingredient_name: str):
        fileObject = open("./assets/JSON/enemies.json", "r")
        fileData = json.load(fileObject)[ingredient_name]

        # Imported Properties
        self.name: str = fileData["name"]
        self.type: str = fileData["type"]
        self.rare_ingredient: bool = fileData["rare_ingredient"]
        self.legendary_ingredient: bool = fileData["legendary_ingredient"]
        self.score: int = fileData["score"]
        self.item_id: int = fileData["item_id"]
        self.type_id: int = 1




# This is the function that sends the ingredients in the inventory, to the database shared inventory
def inv_to_database(connection, room_id, inventory):
    cursor = connection.cursor()

    try:
        for (item_name, quantity) in inventory:

            # look up id
            ingredient = Ingredient(item_name)
            item_id = ingredient.item_id

            # Insert the item into the inventory table
            cursor.execute(
                """
                INSERT INTO inventory (room_id, item_id, quantity)
                VALUES (?, ?, ?)
                """,
                (room_id, item_id, quantity)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        
# Puts the player's inventory of ingredients into a printable format for tk.Stringvar   
def print_ingredients(ingredients: list[tuple[str, int]]) -> str:
    ingredients_str = "Inventory: \n"
    if len(ingredients) > 0:
        for inventory_num in range(len(ingredients)):
            ingredients_str += ingredients[inventory_num][0]
            ingredients_str += ": "
            ingredients_str += str(ingredients[inventory_num][1])
            if inventory_num != (len(ingredients) - 1):
                ingredients_str += ", "
    else:
        ingredients_str = "Nothing in Inventory"
    return ingredients_str