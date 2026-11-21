import mysql.connector

# Allows for creation of an object from the database
class Cookbook:
    def __init__(self, cookbook_name: str, connection):
        self.connection = connection
        cursor = connection.cursor
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
            
        # fileObject = open("../assets/JSON/cookbooks.json", "r")
        # fileData = json.load(fileObject)[cookbook_name]
        
        # self.name = fileData["name"]
        # self.area = fileData["area"]
        # self.price = fileData["price"]
        # self.type_id = 4
        
