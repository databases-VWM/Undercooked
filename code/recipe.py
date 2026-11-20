import json

# Allows for dynamic creation of an object from JSON from just its name
class Recipe:
    def __init__(self, recipe_name: str):
        fileObject = open("../assets/JSON/recipes.json", "r")
        fileData = json.load(fileObject)[recipe_name]

        # Imported Properties
        self.name = fileData["name"]
        self.raw_ingredients: list[list[str]] = fileData["Ingredients"]
        self.required_cookbook: str = fileData["Cookbook"]
        self.workstation: str = fileData["Workstation"]
        
    def display_ingredients(self) -> str:
        ingredients_str = ""
        for i in range(len(self.raw_ingredients)):
            ingredients_str += self.raw_ingredients[i][0] + ": " + self.raw_ingredients[i][1]
            if i != len(self.raw_ingredients) - 1:
                ingredients_str += "\n\t"
        return ingredients_str

    # TODO
    def can_cook(self) -> bool:
        return True