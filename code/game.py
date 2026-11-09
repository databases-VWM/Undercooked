import mysql.connector
import tkinter as tk
from functions import *
from tkinter import messagebox
from entity import *
from area import *

from menu_functions import *

#MySQL default connection
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
        self.room_name = ""
        self.room_ID = None
        self.player: Entity

    # Clears the screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=self.BACKGROUNDCOLOR)

    #Shows the login screen to allow the user to input their ID
    def login(self):
        # GUI and Logic
        self.clear_screen()
        login_label = tk.Label(self.root, text="Please input your User ID to log in!\nOr, create a new user below")
        login_label.pack()
        userID_entry = tk.Entry(self.root)
        userID_entry.pack()
        #Checks for the UserID. If it exists, go to main menu. Else, reopen login
        login_button = tk.Button(self.root, text="Login", command=lambda: self.login_logic(userID_entry.get()))
        login_button.pack()
        register_user_button = tk.Button(self.root, text="Register a New User", command=self.register)
        register_user_button.pack()

    # Handles the logic of the input button
    def login_logic(self, userID):
        self.logged_In = check_user_ID_exists(connection, userID)
        self.userID = userID

        if self.logged_In == True:
            #Creates player
            self.player = Entity("Player", self.userID)
            self.main_menu()
        else:
            self.login()

    # Handles creation of new user
    def register(self):
        self.clear_screen()
        title = tk.Label(self.root, text="Create your user!\nInput your username")
        title.pack()
        username_input = tk.Entry(self.root)
        username_input.pack()
        register_button = tk.Button(self.root, text="Register User!", command=lambda: self.register_user(username_input.get()))
        register_button.pack()

    # Registers a new user
    def register_user(self, username):
        new_user_ID = generate_user_ID(connection)
        create_new_user(connection, new_user_ID, username)
        self.main_menu()


    # Overall main menu
    def main_menu(self):
        self.clear_screen()
        undercooked_title = tk.Label(self.root, text="Welcome to Undercooked!!!")
        undercooked_title.pack()
        create_room_button = tk.Button(self.root, text="Create Room", command=self.create_room_menu)
        create_room_button.pack()
        join_room_button = tk.Button(self.root, text="Join Room", command=self.join_room_menu)
        join_room_button.pack()
        IP_address_button = tk.Button(self.root, text="Show IP Address", command=self.show_IP)
        IP_address_button.pack()
        quit_button = tk.Button(self.root, text="Quit", command=self.quit_game)
        quit_button.pack()

    # Popup that shows the user's IP address and port
    def show_IP(self):
        ip_addr = get_local_ip_and_port()
        IP_popup = messagebox.showinfo(self.root, message=ip_addr)

    # Ends the program
    def quit_game(self):
        self.root.destroy()

    # GUI for creating a room
    def create_room_menu(self):
        self.clear_screen()
        new_room_label = tk.Label(self.root, text="Enter the name of the room")
        new_room_label.pack()
        new_room_name_input = tk.Entry(self.root)
        new_room_name_input.pack()
        create_room_button = tk.Button(self.root, text="Create Room", command=lambda: self.create_room(new_room_name_input.get()))
        create_room_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.main_menu)
        back_button.pack()

    # GUI for joining a room
    def join_room_menu(self):
        self.clear_screen()
        room_IP_button = tk.Entry(self.root)
        room_IP_button.pack()
        room_ID_button = tk.Entry(self.root)
        room_ID_button.pack()
        join_room_button = tk.Button(self.root, text="Join Room", command=lambda: self.join_room(room_ID_button.get(), room_IP_button.get()))
        join_room_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.main_menu)
        back_button.pack()

    # Creates the room in the database
    def create_room(self, room_name):
        new_room_id = generate_room_ID(connection)
        self.room_ID = new_room_id
        self.room_name = room_name
        create_new_room(connection, new_room_id, room_name)
        self.waiting_room_host()

    # Logic for joining an established room
    def join_room(self, room_ID, room_IP):
        connect_to_room(connection, room_ID, room_IP)
        self.waiting_room_guest()

    # The actual waiting room before the game starts for the host
    def waiting_room_host(self):
        self.clear_screen()
        room_name_label = tk.Label(self.root, text=self.room_name)
        room_name_label.pack()
        room_ID_label = tk.Label(self.root, text="ID: " + str(self.room_ID))
        room_ID_label.pack()
        IP_address_button = tk.Button(self.root, text="Show IP Address", command=self.show_IP)
        IP_address_button.pack()
        start_button = tk.Button(self.root, text="Start Game", command=self.restaurant_menu)
        start_button.pack()

    # This is where the guests wait
    def waiting_room_guest(self):
        self.clear_screen()
        room_name_label = tk.Label(self.root, text=self.room_name)
        room_name_label.pack()
        room_ID_label = tk.Label(self.root, text="ID: " + str(self.room_ID))
        room_ID_label.pack()
        IP_address_button = tk.Button(self.root, text="Show IP Address", command=self.show_IP)
        IP_address_button.pack()
        waiting_button = tk.Label(self.root, text="Waiting for host to start game")
        waiting_button.pack()
        #Show all other players in the room, room ID, and room name

    # This is the menu that first opens when the game starts
    def restaurant_menu(self):
        self.clear_screen()
        todo_button = tk.Button(self.root, text="Restaurant Menu is a WIP")
        todo_button.pack()
        rpg_switch_button = tk.Button(self.root, text="To the Wilderness", command=self.wilderness_area_select)
        rpg_switch_button.pack()

    # This is the menu that opens to let the player choose which area they are going to
    def wilderness_area_select(self):
        selected_area = tk.StringVar(self.root)
        selected_area.set("Select an Area")
        unlocked_areas_list = get_item_names("areas")
        select_checkbox = tk.BooleanVar(self.root)
        self.clear_screen()

        wilderness_title = tk.Label(self.root, text="Welcome to the Wilderness!\nSelect an Area!")
        wilderness_title.pack()
        areas_dropdown = tk.OptionMenu(self.root, selected_area, *unlocked_areas_list)
        areas_dropdown.pack()
        checkpoint_checkbox = tk.Checkbutton(self.root, text="Start From Checkpoint?", variable=select_checkbox, onvalue=True, offvalue=False)
        checkpoint_checkbox.pack()
        go_to_wilderness = tk.Button(self.root, text="Go!", command= lambda: self.check_area_select(selected_area.get(), select_checkbox.get()))
        go_to_wilderness.pack()

    # Validates the information provided in wilderness_area_select and selects next menu based on it
    def check_area_select(self, selected_area_name: str, checkpoint_bool: bool) -> None:
        checkpoint_exists: bool = False
        everything_valid: bool = False
        area_message = "You enter " + selected_area_name
        checkpoint_num: int = 1

        #Checks if area was selected. If not, rerun menu
        if selected_area_name == "Select an Area":
            messagebox.showinfo(self.root, message="Please select an area")
            self.wilderness_area_select()
        # If no checkpoint selected (starting from beginning) AND area selected, run next menu
        elif checkpoint_bool == False:
            everything_valid = True
        else:
            for area_tuple in self.player.checkpoints:
                #Successfully finds checkpoint
                if area_tuple[0] == selected_area_name:
                    checkpoint_exists = True
                    area_message = area_message + " at node " + str(area_tuple[1])
                    everything_valid = True
                    checkpoint_num = area_tuple[1]
            # Fails to find checkpoint
            if checkpoint_exists == False:
                messagebox.showinfo(self.root, message="You don't have a checkpoint at that location!")
                self.wilderness_area_select()
        # If checkpoint and area are good, continue
        if everything_valid == True:
            messagebox.showinfo(self.root, message=area_message)
            self.explore_nodes_menu(selected_area_name, checkpoint_num)

    #Function for handling GUI with nodes and rpg logic
    def explore_nodes_menu(self, area_name, checkpoint_num):
        self.clear_screen()
        current_area = Area(area_name)
        if current_area.current_node != checkpoint_num:
            current_area.current_node = checkpoint_num
        current_area.start_rpg()


