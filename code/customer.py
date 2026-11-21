from recipe import *

class Customer:
    def __init__(self, name: str, order: str, room_id: int, connection) -> None:
        self.name = name
        self.order = Recipe(order, connection)
        self.room_id = room_id
        