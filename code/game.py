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

user_ID = generate_user_ID(connection)
print("Generated user ID:", user_ID)

#Holds the game logic
class GameInstance:
    def __init__(self, root):
        self.root = root
        self.BACKGROUNDCOLOR = "lightgray"
        root.state("zoomed")
        root.configure(bg=self.BACKGROUNDCOLOR)


        self.login()
        self.logged_in = False
        self.userID = ""

    # Clears the screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=self.BACKGROUNDCOLOR)

    #Shows the login screen to allow the user to input their ID
    def login(self):
        # GUI and Logic
        self.clear_screen()
        tk.Label(self.root, text="Please input your User ID to log in!\nOr, create a new user below").pack()
        entryText = tk.StringVar()
        userID_entry = tk.Entry(self.root, textvariable=entryText).pack()
        #Checks for the UserID. If it exists, go to main menu. Else, reopen login
        tk.Button(self.root, text="Login", command=lambda: [check_user_ID_exists(connection, entryText.get(), self.logged_in), self.logged_in if self.main_menu else self.login]).pack()
        tk.Button(self.root, text="Register a New User", command=self.register).pack()

    #Screen to create a new user
    def register(self):
        pass

    # Overall main menu
    def main_menu(self):
        self.clear_screen()

        