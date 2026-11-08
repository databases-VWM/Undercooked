import random
import json

# This is a function that just allows for setting values within tkinter commands
def set_value_from_button(buttonValue, newValue):
    newValue = buttonValue

def sample_item(x: list[tuple[str, int]]) -> str:
    return random.choices(x, weights=[i[1] for i in x], k=1)[0]

def get_names(fname: str) -> list[str]:
    with open("../assets/JSON/" + fname, "r") as file_object:
        return list(json.load(file_object).keys())
