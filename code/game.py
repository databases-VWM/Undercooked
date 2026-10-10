import mysql.connector
import tkinter as tk

from menu_functions import *

#MySQL connection
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

        self.login()
        self.userID = ""

    # Clears the screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=self.BACKGROUNDCOLOR)

    #Shows the login screen to allow the user to input their ID
    def login(self):
        # Widget names
        userID_entry

        # GUI and Logic
        self.clear_screen()
        tk.Label(self.root, text="Please input your User ID to log in!\nOr, create a new user below").pack()
        userID_entry = tk.Entry(self.root).pack()
        tk.Button(self.root, text="Login", command=self.main_menu).pack()
        tk.Button(self.root, text="Register a New User").pack()

    #Screen to create a new user
    def register(self):
        pass

    # Overall main menu
    def main_menu(self):
        self.clear_screen()

        