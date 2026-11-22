import mysql.connector
from ingredient import Ingredient
from weapon import Weapon
from armor import Armor
from customer import *
import random


# I want to make a class as If we need to access database information multiple times, it simplifies the code to be able to store it somewhere.
# All we would need to to is call update_restaurant before anything to make it up to date
class Restaurant:
    def __init__(self, restaurant_name, room_id, connection):
        self.restaurant_name = restaurant_name
        self.room_id = room_id
        self.connection = connection

        self.max_customers = 0
        self.money = 1000
        self.day = 0
        self.time = 0
        self.reputation = 0

        self.areas_unlocked = []

        # List of one-time purchases already made. Stores the by id
        self.onetime_purchases: list[str] = []
        self.unlocked_recipes = []
        self.customers: list[Customer] = []

        # List of tuples: (item_name, quantity)
        self.inventory: list[tuple[int, int, str, int]] = [] # NOTE this may be redundant

        self.update_restaurant()

    def update_restaurant(self):
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                SELECT current_money, game_day, day_time, reputation
                FROM rooms
                WHERE room_id = %s
                """,
                (self.room_id,)
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError(f"No restaurant found with room_id {self.room_id}")

            self.money = result[0]
            self.day = result[1]
            self.time = result[2]
            self.reputation = result[3]

            # cookbook names that are unlocked
            cursor.execute(
                """
                SELECT cookbook_name
                FROM unlocked_cookbooks
                WHERE room_id = %s
                """,
                (self.room_id,)
            )

            self.onetime_purchases = [
                row[0] for row in cursor.fetchall()
            ]

        finally:
            cursor.close()

        # Retrieve inventory
        self.inventory = self.access_inventory()



    def access_inventory(self):
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                SELECT type_id, item_id, item_name, quantity
                FROM inventory
                WHERE room_id = %s
                """,
                (self.room_id, )
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            
    # Returns everything in the inventory of a certain type_id
    def access_database_inventory_filter_type_id(self, type_id) -> list[tuple[int, int, str, int]]:
        cursor = self.connection.cursor()
        inventory_list: list[tuple[int, int, str, int]] = []
        try:
            cursor.execute(
                """
                SELECT type_id, item_id, item_name, quantity
                FROM inventory
                WHERE room_id = %s AND type_id = %s
                """,
                (self.room_id, type_id)
            )

            inventory_tuples = cursor.fetchall()
            for i in range(len(inventory_tuples)):
                item_type_id = inventory_tuples[i][0]
                item_id = inventory_tuples[i][1]
                item_name = inventory_tuples[i][2]
                item_quantity = inventory_tuples[i][3]
                inventory_list.append(tuple([item_type_id, item_id, item_name, item_quantity]))
            
            return inventory_list

        finally:
            cursor.close()

    # type_id, item_id,item_name, quantity 
    def add_item(self, items: list[tuple[int, int, str, int]]):
        cursor = self.connection.cursor()

        try:
            for type_id, item_id, item_name, quantity in items:

                cursor.execute(
                    """
                    CALL add_inventory_item(%s, %s, %s, %s, %s)
                    """,
                    (type_id, item_id, item_name, quantity, self.room_id)
                    # """
                    # INSERT INTO inventory (type_id, item_id, item_name, quantity, room_id)
                    # VALUES (%s, %s, %s, %s, %s)
                    # """,
                )

            self.connection.commit()

            # Refresh local inventory
            self.inventory = self.access_inventory()

            return True

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()



    # function that removes item tuple
    # (typeid itemid name quantity)
    # Vincent, this is that functiion
    def remove_item(self, items: list[tuple[int, int, int]]):
        cursor = self.connection.cursor()

        self.update_restaurant()

        try:
            # First, validate that every requested item exists locally
            for type_id, item_id, quantity in items:
                found = False

                for inv_type, inv_id, inv_name, inv_quantity in self.inventory:
                    if inv_type == type_id and inv_id == item_id:
                        found = True

                        # Not enough quantity
                        if inv_quantity < quantity:
                            return False

                        break

                # Item doesn't exist in inventory
                if not found:
                    return False

            # All items are available, so remove them
            for type_id, item_id, quantity in items:
                cursor.execute(
                    """
                    CALL remove_inventory_item(%s, %s, %s, %s)
                    """,
                    (type_id, item_id, quantity, self.room_id)
                )

            self.connection.commit()

            # Refresh local inventory
            self.inventory = self.access_inventory()

            return True

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()

    # Generic function to display inventory
    def display_inventory(self):
        # Refresh inventory from database
        self.inventory = self.access_inventory()

        inventory_str = ""

        if len(self.inventory) > 0:
            for inventory_num in range(len(self.inventory)):
                inventory_str += str(self.inventory[inventory_num][0])
                inventory_str += ": "
                inventory_str += str(self.inventory[inventory_num][1])
                if inventory_num != (len(self.inventory) - 1):
                    inventory_str += "\n "
        else:
            inventory_str = "Nothing in Inventory"
        return inventory_str
    
    # def display_inventory(self, id_in):
    #         # Refresh inventory from database
    #         self.inventory = self.access_inventory()
    
    #         display_list = []
    
    #         for type_id, item_id, item_name, quantity in self.inventory:
    #             if (type_id == id_in):
    #                 display_list.append((item_name, quantity))
                
    
    #         return display_list
    
    # Updates money in the database
    def update_money(self):
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                "UPDATE rooms SET current_money = %s WHERE room_id = %s",
                (self.money, self.room_id)
            )
            
            self.update_restaurant()
        finally:
            cursor.close()
            
    # Unlocks a ourchased cookbook in the database
    def unlock_cookbook(self, cookbook_name: str) -> None:
        cursor = self.connection.cursor()
        self.onetime_purchases.append(cookbook_name)

        try:
            cursor.execute(
                "INSERT INTO unlocked_cookbooks VALUES(%s, %s)",
                (cookbook_name, self.room_id)
            )
        finally:
            cursor.close()
            
    # Retrieves all customer tuples and returns their values
    def update_customer_orders_from_database(self) -> None:
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM customers WHERE room_id = %s",
                (self.room_id, )
            )
            
            customer_tuples = cursor.fetchall()
            for customer in customer_tuples:
                self.customers.append(Customer(customer[0], customer[2], customer[1], self.connection))
        finally:
            cursor.close()
            
    # For a given customer, return a list of strings containing their name, order, and required ingredients to cook their order
    # This is for listbox
    def display_customer_order_list(self) -> list[str]:
        customer_order_list: list[str] = []
        for i in range(len(self.customers)):
            customer_str = ""
            customer_str += self.customers[i].name
            customer_str += " is ordering "
            customer_str += self.customers[i].order.name
            customer_str += "\nThis requires: "
            customer_str += self.customers[i].order.display_ingredients()
            customer_order_list.append(customer_str)
        return customer_order_list
    
    # Function to handle the generation of customers
    def create_customers(self, num_players: int) -> None:
        # Determines the amount of customers to be generated on a given day
        self.max_customers = self.day * num_players
        # Loops for customer generation
        for i in range(self.max_customers):
            new_customer: Customer
            new_customer_name = self.make_customer_name()
            new_customer_order = self.make_customer_order()
            new_customer = Customer(new_customer_name, new_customer_order, self.room_id, self.connection)
            # Checks to see if the generated customer already exists. If so, generates a new one
            while(new_customer.still_exist()):
                new_customer_name = self.make_customer_name()
                new_customer_order = self.make_customer_order()
                new_customer = Customer(new_customer_name, new_customer_order, self.room_id, self.connection)
            # Actually pushes new customer to the database
            new_customer.push_to_database()
            
    def make_customer_name(self) -> str:
        # I had Claude generate this list
        names_list = [
            "Liam", "Olivia", "Noah", "Emma", "Oliver", "Ava", "Elijah", "Sophia", "James", "Isabella",
            "William", "Mia", "Benjamin", "Charlotte", "Lucas", "Amelia", "Henry", "Harper", "Theodore", "Evelyn",
            "Jack", "Abigail", "Levi", "Emily", "Alexander", "Ella", "Mason", "Scarlett", "Ethan", "Grace",
            "Daniel", "Chloe", "Jacob", "Victoria", "Michael", "Riley", "Logan", "Aria", "Owen", "Lily",
            "Samuel", "Aurora", "Sebastian", "Zoey", "Caleb", "Penelope", "Ryan", "Layla", "Nathan", "Nora",
            "Isaac", "Hazel", "Leo", "Luna", "Hudson", "Stella", "Wyatt", "Ellie", "Gabriel", "Violet",
            "Julian", "Willow", "Dylan", "Naomi", "Asher", "Savannah", "Carter", "Brooklyn", "Jayden", "Bella",
            "Grayson", "Claire", "Lincoln", "Skylar", "Anthony", "Lucy", "Eli", "Paisley", "Joshua", "Everly",
            "Christopher", "Anna", "Andrew", "Caroline", "Thomas", "Nova", "Joseph", "Genesis", "Hunter", "Aaliyah",
            "Adrian", "Kennedy", "Ezra", "Maya", "Miles", "Sarah", "Easton", "Madelyn", "Declan", "Adeline",
            "Vincent", "Max", "Wesley"
        ]
        return random.choice(names_list)
    
    def make_customer_order(self) -> str:
        unlocked_recipes_list = self.get_available_recipes()
        return random.choice(unlocked_recipes_list)
    
    # This checks all unlocked recipes in the database for the room and returns a list of them
    def get_available_recipes(self) -> list[str]:
        recipe_names_list: list [str] = []
        cursor = self.connection.cursor()
        try:
            # First, retrieve all recipes that don't require a cookbook
            cursor.execute(
                "SELECT recipe_name FROM recipes WHERE cookbook_name IS NULL"
            )
            no_cookbook_recipe_list = cursor.fetchall()
            # Append to overall list
            for db_tuple in no_cookbook_recipe_list:
                recipe_names_list.append(db_tuple[0])
                
            cursor.execute(
                "SELECT recipe_name FROM recipes NATURAL JOIN (SELECT * FROM cookbooks NATURAL JOIN unlocked_cookbooks WHERE room_id = %s) AS unlocked_cookbooks;",
                (self.room_id, )
            )
            # Appends anything found that uses an unlocked cookbook
            yes_cookbook_recipe_list = cursor.fetchall()
            if yes_cookbook_recipe_list != None:
                for db_tuple in yes_cookbook_recipe_list:
                    recipe_names_list.append(db_tuple[0])
            return recipe_names_list
            
        finally:
            cursor.close()