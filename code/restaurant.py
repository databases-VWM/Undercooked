import mysql.connector
from ingredient import Ingredient
from weapon import Weapon
from armor import Armor


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
                FROM cookbooks
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
                (self.room_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()

    def add_item(self, items):
        cursor = self.connection.cursor()

        try:
            for type_id, item_id, item_name, quantity in items:

                cursor.execute(
                    """
                    INSERT INTO inventory (type_id, item_id, item_name, quantity, room_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (type_id, item_id, item_name, quantity, self.room_id)
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



    # function that removes item
    def remove_item(self, items):
        cursor = self.connection.cursor()

        try:
            # First, validate that every requested item exists
            for type_id, item_id, quantity in items:

                cursor.execute(
                    """
                    SELECT quantity
                    FROM inventory
                    WHERE room_id = %s
                    AND type_id = %s
                    AND item_id = %s
                    """,
                    (self.room_id, type_id, item_id)
                )

                result = cursor.fetchone()

                # Item isnt in inventory, or there isnt enough quantity
                if result is None or result[0] < quantity:
                    self.connection.rollback()
                    return False

            # All items are available, so remove them
            for type_id, item_id, quantity in items:

                cursor.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity - %s
                    WHERE room_id = %s
                    AND type_id = %s
                    AND item_id = %s
                    """,
                    (quantity, self.room_id, type_id, item_id)
                )

                # Delete entry if quantity reaches zero
                cursor.execute(
                    """
                    DELETE FROM inventory
                    WHERE room_id = %s
                    AND type_id = %s
                    AND item_id = %s
                    AND quantity = 0
                    """,
                    (self.room_id, type_id, item_id)
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

def display_inventory(self, id_in):
    # Refresh inventory from database
    self.inventory = self.access_inventory()

    display_list = []

    for type_id, item_id, item_name, quantity in self.inventory:
        if (type_id == id_in):
            display_list.append((item_name, quantity))
        

    return display_list