from recipe import *

class Customer:
    def __init__(self, name: str, order: str, room_id: int, connection) -> None:
        self.connection = connection
        self.name = name
        self.order = Recipe(order, connection)
        self.room_id = room_id
        
    def still_exist(self) -> bool:
        cursor = self.connection.cursor()
        try: 
            cursor.execute(
                "SELECT * FROM customers WHERE customer_name = %s AND recipe_name = %s AND room_id = %s",
                (self.name, self.order.name, self.room_id)
            )
            
            result = cursor.fetchone()
            if result == None:
                return False
            else:
                return True
            
        finally: 
            cursor.close()
    
    # Deletes a customer from the database
    def delete(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM customers WHERE room_id = %s AND customer_name = %s",
                (self.room_id, self.name)
            )
            self.connection.commit()
        except:
            self.connection.rollback()
        finally:
            cursor.close()
    
    # Pushes the customer to the database
    def push_to_database(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO customers VALUES (%s, %s, %s)",
                (self.name, self.room_id, self.order.name)
            )
            self.connection.commit()
        except:
            self.connection.rollback()
        finally:
            cursor.close()