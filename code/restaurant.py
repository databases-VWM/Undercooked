import mysql.connector
from ingredient import Ingredient
from weapon import Weapon
from armor import Armor
from customer import *


# I want to make a class as If we need to access database information multiple times, it simplifies the code to be able to store it somewhere.
# All we would need to to is call update_restaurant before anything to make it up to date
class Restaurant:
    def __init__(self, restaurant_name, room_id, connection):
        self.restaurant_name = restaurant_name
        self.room_id = room_id
        self.connection = connection

        self.money = 1000
        self.day = 0
        self.time = 0

        self.areas_unlocked = []

        # List of one-time purchases already made. Stores the by id
        self.onetime_purchases: list[str] = []
        self.unlocked_recipes = []
        self.customers: list[Customer] = []

        # List of tuples: (item_name, quantity)
        self.inventory: list[tuple[str, int]] = [] # NOTE this may be redundant

        self.update_restaurant()

    def update_restaurant(self):
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                SELECT current_money, game_day, day_time
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
            
    def access_database_inventory_filter_type_id(self, type_id):
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                SELECT type_id, item_id, item_name, quantity
                FROM inventory
                WHERE room_id = %s AND type_id = %s
                """,
                (self.room_id, type_id)
            )

            return cursor.fetchall()

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
    def remove_item(self, items: list[tuple[int, int, int]]):
        cursor = self.connection.cursor()

        self.update_restaurant()

        try:
            # First, validate that every requested item exists locally
            # for type_id, item_id, quantity in items:
                
                
                # I think this is redundant. The procedure handles this
                # found = False

                # for inv_type, inv_id, inv_name, inv_quantity in self.inventory:
                #     if inv_type == type_id and inv_id == item_id:
                #         found = True

                #         # Not enough quantity
                #         if inv_quantity < quantity:
                #             return False

                #         break

                # # Item doesn't exist in inventory
                # if not found:
                #     return False

            # All items are available, so remove them
            for type_id, item_id, quantity in items:

                cursor.execute(
                    """
                    CALL remove_inventory_item(%s, %s, %s, %s)
                    """,
                    (type_id, item_id, quantity, self.room_id)
                ) 



                
                # cursor.execute(
                #     """
                #     UPDATE inventory
                #     SET quantity = quantity - %s
                #     WHERE room_id = %s
                #     AND type_id = %s
                #     AND item_id = %s
                #     """,
                #     (quantity, self.room_id, type_id, item_id)
                # )

                # # Delete entry if quantity reaches zero
                # cursor.execute(
                #     """
                #     DELETE FROM inventory
                #     WHERE room_id = %s
                #     AND type_id = %s
                #     AND item_id = %s
                #     AND quantity = 0
                #     """,
                #     (self.room_id, type_id, item_id)
                # )

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
                inventory_str += self.inventory[inventory_num][0]
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
                self.customers.append(Customer(customer[0], customer[2], customer[1]))
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
            