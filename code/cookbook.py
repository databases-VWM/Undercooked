import mysql.connector

# Allows for creation of an object from the database
class Cookbook:
    def __init__(self, cookbook_name: str, connection):
        self.connection = connection
        cursor = connection.cursor()
        self.name = cookbook_name
        self.type_id = 4
        try:
            cursor.execute(
                "SELECT * FROM cookbooks WHERE cookbook_name = %s",
                (cookbook_name, )
            )
            db_cookbook = cursor.fetchone()
            self.area: str = db_cookbook[1]
            self.price: int = db_cookbook[2]
        finally:
            cursor.close()

# Returns the names of all cookbooks
def get_cookbook_names(connection) -> list[str]:
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "SELECT cookbook_name FROM cookbooks"
        )
        cookbooks_list: list[str] = []
        cookbooks_tuples = cursor.fetchall()
        for cookbook in cookbooks_tuples:
            cookbooks_list.append(cookbook[0])
        return cookbooks_list
    finally:
        cursor.close()
