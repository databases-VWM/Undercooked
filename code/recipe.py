import mysql.connector

# Allows for dynamic creation of an object from the database
class Recipe:
    def __init__(self, recipe_name: str, connection):
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM recipes WHERE recipe_name = %s",
                (recipe_name, )
            )
            self.name = recipe_name
            recipe_tuple = cursor.fetchone()
            self.required_cookbook = recipe_tuple[1]
            self.price = recipe_tuple[2]
            # string lists contain [ingredient name, quantity(str)]
            self.raw_ingredients: list[list[str]] = []
            
            cursor.execute(
                "SELECT * FROM recipe_ingredients WHERE recipe_name = %s",
                (recipe_name, )
            )
            ingredients_tuples_list = cursor.fetchall()
            
            for ingredients_tuple in ingredients_tuples_list:
                ingredient_list: list[str] = []
                ingredient_list.append(ingredients_tuple[1])
                ingredient_list.append(ingredients_tuple[2])
                self.raw_ingredients.append(ingredient_list)
            
        finally:
            cursor.close()
        # fileObject = open("../assets/JSON/recipes.json", "r")
        # fileData = json.load(fileObject)[recipe_name]

        # # Imported Properties
        # self.name = fileData["name"]
        # self.raw_ingredients: list[list[str]] = fileData["Ingredients"]
        # self.required_cookbook: str = fileData["Cookbook"]
        # self.workstation: str = fileData["Workstation"]
        
    def display_ingredients(self) -> str:
        ingredients_str = ""
        for i in range(len(self.raw_ingredients)):
            ingredients_str += str(self.raw_ingredients[i][0]) + ": " + str(self.raw_ingredients[i][1])
            if i != len(self.raw_ingredients) - 1:
                ingredients_str += "\n\t"
        return ingredients_str
