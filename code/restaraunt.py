
import mysql.connector
from ingredient import Ingredient


# I want to make a class as If we need to access database information multiple times, it simplifies the code to be able to store it somewhere.
# All we would need to to is call update_restauraunt before anything to make it up to date
class Restaraunt:
    def __init__(self, restaraunt_name, room_id: int, connection):
        self.restaraunt_name = restaraunt_name
        self.room_id = room_id
        self.connection = connection

        self.areas_unlocked = []

        # List of one-time purchases already made
        self.onetime_purchases = []

        # List of tuples: (item_name, quantity)
        self.inventory = [] # NOTE this may be redundant

        self.update_restauraunt()

    def update_restauraunt(self):
        # Retrieves all relevant information to update the restaurant class
        # should check the shop for booleans for unlocks and add them to onetime_purchases

        # Will finish implementation later

        # Retrieve inventory
        self.inventory = self.access_inventory()

        # Continue retrieving other restaurant information here
        # when those database tables are implemented.

    def access_inventory(self):
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """
                SELECT type_id, item_id, quantity
                FROM inventory
                WHERE room_id = %s
                """,
                (self.room_id,)
            )

            # Returns a list of tuples
            # (type_id, item_id, quantity)
            return cursor.fetchall()

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