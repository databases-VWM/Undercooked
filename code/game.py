import mysql.connector
from menu_functions import *
connection = mysql.connector.connect(
    host="localhost",
    user="game",
    password="pancake_sandwich",
    database="undercooked"
)

player_ID = generate_player_ID(connection)
print("Generated player ID:", player_ID)
    
#Holds the game logic
class GameInstance:
    def __init__(self, root):
        self.root = root
        self.BACKGROUNDCOLOR = "lightgray"
        root.state("zoomed")
        root.configure(bg=self.BACKGROUNDCOLOR)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=self.BACKGROUNDCOLOR)

    def main_menu(self):
        self.clear_screen()
        