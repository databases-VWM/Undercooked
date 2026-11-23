import random
import json
from tkinter import messagebox

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

# Retrieves the ID of an ingredient from its name
def get_ingredient_id_from_name(connection, item_name) -> int:
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT ingredient_id FROM ingredients WHERE ingredient_name = %s",
            (item_name, )
        )
        ingredient_tuple = cursor.fetchone()
        return ingredient_tuple[0]
    finally:
        cursor.close()
        

# Database editor functions:

# Submits a new ingredient entry into the database
def submit_editor_ingredient(connection, ingredient_name: str, ingredient_type: str):
    cursor = connection.cursor()
    if ingredient_name == None or ingredient_type == None:
        messagebox.showerror(message="There was an error and nothing was added to the database")
        return
    try:
        cursor.execute(
            "SELECT max(ingredient_id) FROM ingredients"
        )
        max_id = cursor.fetchone()
        
        cursor.execute(
            "INSERT INTO ingredients VALUES(%s, %s, %s)",
            (max_id + 1, ingredient_name, ingredient_type)
        )
        
        connection.commit()
        messagebox.showinfo(message=f"You successfully added {ingredient_name} to the database!")
        
    except:
        messagebox.showerror(message="There was an error and nothing was added to the database")
        connection.rollback()
    finally:
        cursor.close()
        
# Submits a new ingredient_area entry into the database
def submit_editor_ingredient_area(connection, ingredient_name: str, area: str, weight):
    cursor = connection.cursor()
    try:
        ingredient_id = get_ingredient_id_from_name(connection, ingredient_name)
        
        cursor.execute(
            "INSERT INTO area_ingredients VALUES(%s, %s, %s)",
            (area, ingredient_id, weight)
        )
        
        connection.commit()
        messagebox.showinfo(message=f"You successfully added {ingredient_name} to {area} in the database!")
        
    except:
        messagebox.showerror(message="There was an error and nothing was added to the database\nMake sure your ingredient doesn't already exist in an area\nAlso make sure your weight is an integer value")
        connection.rollback()
    finally:
        cursor.close()

def submit_editor_area(connection, area_name: str, area_power):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO areas VALUES(%s, %s)",
            (area_name, area_power)
        )
        connection.commit()
        messagebox.showinfo(message=f"You have successfully inserted {area_name} into the database")
    except:
        messagebox.showerror(message="There was an error and nothing was added to the database\nMake sure your area and power combo doesn't already exist\nBe sure your power is an integer")
        connection.rollback()
    finally:
        cursor.close()
        
def submit_editor_cookbook(connection, name, area, price):
    cursor= connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO cookbooks VALUES(%s, %s, %s)",
            (name, area, price)
        )
        connection.commit()
        messagebox.showinfo(message=f"Your cookbook, {name} has been successfully added to the database")
    except:
        connection.rollback()
        messagebox.showerror(message="There was an error and nothing was added to the database")
    finally:
        cursor.close()
       
# Submits a custom recipe to the database 
def submit_editor_recipe(connection, recipe_name, cookbook, price):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO recipes VALUES(%s, %s, %s)",
            (recipe_name, cookbook, price)
        )
        connection.commit()
        messagebox.showinfo(message=f"Your recipe, {recipe_name}, was successfully added to the database")
    except:
        messagebox.showerror(message="There was an error and nothing was added to the database\nMake sure it doesn't already exist\nEnsure that your price is an integer")
        connection.rollback()
    finally:
        cursor.close()

# Submits to the recipe_ingredient junction table
def submit_editor_recipe_ingredient(connection, recipe_name, ingredient_name, quantity):
    cursor = connection.cursor()
    try:
        ingredient_id = get_ingredient_id_from_name(connection, ingredient_name)
        cursor.execute(
            "INSERT INTO recipe_ingredients VALUES(%s, %s, %s)",
            (recipe_name, ingredient_id, quantity)
        )
        connection.commit()
        messagebox.showinfo(message=f"You successfully added {ingredient_id} to be required to cook {recipe_name}")
    except:
        messagebox.showerror(message="Something went wrong. Nothing was added to the database")
        connection.rollback()
    finally:
        cursor.close()

# Submits enemy to the database
def submit_editor_enemy(connection, name, health, defense, is_boss, description):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO enemies VALUES(%s, %s, %s, %s, %s)",
            (name, health, defense, is_boss, description)
        )
        connection.commit()
        messagebox.showinfo(message=f"You successfully added {name} to the database!")
    except: 
        messagebox.showerror(message="Something went wrong. Nothing was added to the database")
        connection.rollback()
    finally:
        cursor.close()

# Submits an enemy's attack dice to the database
def submit_editor_enemy_attack_dice(connection, enemy_name, num_dice, num_sides):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO enemy_attack_dice VALUES(%s, %s, %s)",
            (enemy_name, num_dice, num_sides)
        )
        connection.commit()
        messagebox.showinfo(message=f"Your enemy's attack dice were successfully added to the database")
    except:
        connection.rollback()
        messagebox.showerror(message="Something went wrong. Nothing was added to the database")
    finally:
        cursor.close()
        
# Adds an enemy to an area in the database
def submit_editor_add_enemy_to_area(connection, area_name, enemy_name, weight):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO area_enemies VALUES(%s, %s, %s)",
            (area_name, enemy_name, weight)
        )
        connection.commit()
        messagebox.showinfo(message=f"{enemy_name} was added to {area_name}")
    except:
        connection.rollback()
        messagebox.showerror(message="Something went wrong. Nothing was added to the database")
    finally:
        cursor.close()