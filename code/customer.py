from recipe import *

class Customer:
    def __init__(self, name: str, order: str, room_id: int) -> None:
        self.name = name
        self.order = Recipe(order)
        self.room_id = room_id
        