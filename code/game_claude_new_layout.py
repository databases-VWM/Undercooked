import mysql.connector
import tkinter as tk
import sys
from functions import *
from tkinter import messagebox
from entity import *
from area import *
from ingredient import *
from combat import *
from menu_functions import *
import bcrypt
import json
from weapon import *
from armor import * 
from cookbook import *
from restaurant import *

#Holds the game logic
class GameInstance:
    def __init__(self, root):
        self.root = root
        self.BACKGROUNDCOLOR = "#f5efe0"

        # ---------- GUI style constants (change these to restyle the whole game) ----------
        # Colors
        self.PANEL_COLOR = "#fffaf0"
        self.TEXT_COLOR = "#3b2f2f"
        self.BUTTON_COLOR = "#c0392b"
        self.BUTTON_ACTIVE_COLOR = "#e74c3c"
        self.BUTTON_TEXT_COLOR = "white"
        self.SELECT_COLOR = "#e67e22"
        self.ENTRY_COLOR = "white"
        # Fonts
        self.FONT_FAMILY = "Helvetica"
        self.TITLE_FONT = (self.FONT_FAMILY, 18, "bold")
        self.BODY_FONT = (self.FONT_FAMILY, 12)
        self.BUTTON_FONT = (self.FONT_FAMILY, 11, "bold")
        # Sizes and spacing
        self.PAD_X = 10
        self.PAD_Y = 6
        self.WRAP_LENGTH = 700
        self.PANEL_WRAP_LENGTH = 400
        self.BUTTON_WIDTH = 24
        self.BUTTON_WRAP_LENGTH = 200
        self.ENTRY_WIDTH = 30
        self.LISTBOX_WIDTH = 30
        self.LISTBOX_HEIGHT = 12
        self.LISTBOX_SHORT_HEIGHT = 4

        # Widget style groups (unpacked into the widgets with **)
        self.FRAME_STYLE = {"bg": self.BACKGROUNDCOLOR}
        # Big headings
        self.TITLE_STYLE = {"font": self.TITLE_FONT, "bg": self.BACKGROUNDCOLOR, "fg": self.TEXT_COLOR,
                            "wraplength": self.WRAP_LENGTH, "justify": "center"}
        # Normal text
        self.LABEL_STYLE = {"font": self.BODY_FONT, "bg": self.BACKGROUNDCOLOR, "fg": self.TEXT_COLOR,
                            "wraplength": self.WRAP_LENGTH, "justify": "center"}
        # Boxed text used for stats, logs, and inventories
        self.PANEL_STYLE = {"font": self.BODY_FONT, "bg": self.PANEL_COLOR, "fg": self.TEXT_COLOR,
                            "relief": "solid", "bd": 1, "padx": 12, "pady": 8,
                            "wraplength": self.PANEL_WRAP_LENGTH, "justify": "left"}
        self.BUTTON_STYLE = {"font": self.BUTTON_FONT, "bg": self.BUTTON_COLOR, "fg": self.BUTTON_TEXT_COLOR,
                             "activebackground": self.BUTTON_ACTIVE_COLOR, "activeforeground": self.BUTTON_TEXT_COLOR,
                             "relief": "flat", "bd": 0, "padx": 12, "pady": 6, "cursor": "hand2",
                             "width": self.BUTTON_WIDTH, "wraplength": self.BUTTON_WRAP_LENGTH}
        self.ENTRY_STYLE = {"font": self.BODY_FONT, "bg": self.ENTRY_COLOR, "fg": self.TEXT_COLOR,
                            "relief": "solid", "bd": 1, "width": self.ENTRY_WIDTH, "justify": "center"}
        self.LISTBOX_STYLE = {"font": self.BODY_FONT, "bg": self.ENTRY_COLOR, "fg": self.TEXT_COLOR,
                              "selectbackground": self.SELECT_COLOR, "selectforeground": self.BUTTON_TEXT_COLOR,
                              "relief": "solid", "bd": 1, "highlightthickness": 0, "activestyle": "none"}
        self.CHECKBUTTON_STYLE = {"font": self.BODY_FONT, "bg": self.BACKGROUNDCOLOR, "fg": self.TEXT_COLOR,
                                  "activebackground": self.BACKGROUNDCOLOR, "activeforeground": self.TEXT_COLOR,
                                  "selectcolor": self.PANEL_COLOR}
        self.OPTIONMENU_STYLE = {"font": self.BODY_FONT, "bg": self.ENTRY_COLOR, "fg": self.TEXT_COLOR,
                                 "activebackground": self.SELECT_COLOR, "activeforeground": self.BUTTON_TEXT_COLOR,
                                 "relief": "solid", "bd": 1, "highlightthickness": 0, "width": 24}
        # Pack spacing groups
        self.TITLE_PACK = {"padx": self.PAD_X, "pady": 15}
        self.LABEL_PACK = {"padx": self.PAD_X, "pady": self.PAD_Y}
        self.BUTTON_PACK = {"padx": self.PAD_X, "pady": self.PAD_Y}
        # --------------------------------------------------------------------------------

        root.state("zoomed" if sys.platform == "win32" else "normal")
        root.configure(bg=self.BACKGROUNDCOLOR)

        # Starting screen
        self.database_select_screen()
        self.logged_in = False
        self.userID = ""
        self.room_name = ""
        self.room_ID = None
        self.player: Entity
        self.current_enemy: Entity
        self.is_host: bool = False
        self.num_players: int = 1
        # list of tuples of (ingredient name, quantity)
        self.local_inventory: list[tuple[str, int]] = []
        self.current_area: Area
        self.checkpoints: dict[str, int] = {}
        self.combat_log: list[str] = []
        self.connection = None
        self.restaurant_obj: Restaurant
        self.weapon: Weapon = Weapon("Frying Pan")
        self.armor: Armor = Armor("Chef's Garbs")
        
        # Constant for deciding how many seconds long each day should be
        self.TIME_CONSTRAINT_SECONDS = 120
        # Scalar basis for how much daily rent is
        self.RENT_SCALAR = 10

    # Clears the screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            del widget
        self.root.configure(bg=self.BACKGROUNDCOLOR)

    #This lets the player, at game start, choose which database they are connecting to
    def database_select_screen(self):
        self.clear_screen()
        # Centered frame that holds this screen's widgets
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        database_label = tk.Label(menu_frame, text="Please select which database you are playing on. If you are hosting, leave all these values as their defaults", **self.LABEL_STYLE)
        database_label.pack(**self.LABEL_PACK)
        ip_addr_label = tk.Label(menu_frame, text="IP Address:", **self.LABEL_STYLE)
        ip_addr_label.pack(**self.LABEL_PACK)
        ip_addr_entry = tk.Entry(menu_frame, **self.ENTRY_STYLE)
        #Sets default text
        ip_addr_entry.insert(0, "localhost")
        ip_addr_entry.pack(**self.LABEL_PACK)
        # port_label = tk.Label(self.root, text="Port:")
        # port_label.pack()
        # port_entry = tk.Entry(self.root)
        # port_entry.insert(0, "3306")
        # port_entry.pack()
        continue_button = tk.Button(menu_frame, text="Continue", command= lambda: [self.setup_database_connection(ip_addr_entry.get()), self.login()], **self.BUTTON_STYLE)
        continue_button.pack(**self.BUTTON_PACK)
        
    # Sets up the database connection
    def setup_database_connection(self, ip_addr):
        try:
            self.connection = mysql.connector.connect(
                host=ip_addr,
                user="game",
                password="pancake_sandwich",
                database="undercooked"
            )
        except:
            messagebox.showerror(message="Database not running. Exiting game now")
            sys.exit(1)

    #Shows the login screen to allow the user to input their ID
    def login(self):
        # GUI and Logic
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        login_label = tk.Label(menu_frame, text="Please input your User ID and password to login!\nOr, create a new user below", **self.LABEL_STYLE)
        login_label.pack(**self.LABEL_PACK)
        userID_entry = tk.Entry(menu_frame, **self.ENTRY_STYLE)
        userID_entry.pack(**self.LABEL_PACK)
        password_entry = tk.Entry(menu_frame, show="*", **self.ENTRY_STYLE)
        password_entry.pack(**self.LABEL_PACK)
        #Checks for the UserID. If it exists, go to main menu. Else, reopen login
        login_button = tk.Button(menu_frame, text="Login", command=lambda: self.login_logic(userID_entry.get(), password_entry.get()), **self.BUTTON_STYLE)
        login_button.pack(**self.BUTTON_PACK)
        register_user_button = tk.Button(menu_frame, text="Register a New User", command=self.register, **self.BUTTON_STYLE)
        register_user_button.pack(**self.BUTTON_PACK)

    # Handles the logic of the input button
    def login_logic(self, userID: str, password: str):
        correct_login = check_login_info(self.connection, userID, password)
        if correct_login == True:
            # Checks to see if the user already has a connection
            if is_logged_in(self.connection, userID) == False:
                self.userID = userID
                #Creates player
                self.player = Entity("Player", self.connection, True)
                # Sets player name from database
                self.player.name = get_username(self.connection, self.userID)
                self.main_menu()
            else: 
                self.duplicate_connection(userID, password)
            # self.main_menu() # This is only here for testing purposes
        else:
            messagebox.showerror(message=" Failed to login. Please check your username and password and try again")
            self.login()

    # Checks for and handles duplicate connections
    def duplicate_connection(self, userID, password):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        duplicate_connection_label = tk.Label(menu_frame, text="You are already logged in somewhere else. Would you like to make a new connection?", **self.LABEL_STYLE)
        duplicate_connection_label.pack(**self.LABEL_PACK)
        yes_connect_button = tk.Button(menu_frame, text="Yes", command= lambda: [set_log_in(self.connection, False, userID), self.login_logic(userID, password)], **self.BUTTON_STYLE)
        yes_connect_button.pack(**self.BUTTON_PACK)
        no_connect_button = tk.Button(menu_frame, text="No", command=self.login, **self.BUTTON_STYLE)
        no_connect_button.pack(**self.BUTTON_PACK)

    # Handles creation of new user
    def register(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        title = tk.Label(menu_frame, text="Create your user!\nInput your username", **self.LABEL_STYLE)
        title.pack(**self.LABEL_PACK)
        username_input = tk.Entry(menu_frame, **self.ENTRY_STYLE)
        username_input.pack(**self.LABEL_PACK)
        password_entry = tk.Entry(menu_frame, show="*", **self.ENTRY_STYLE)
        password_entry.pack(**self.LABEL_PACK)
        register_button = tk.Button(menu_frame, text="Register User!", command=lambda: self.register_user(username_input.get(), password_entry.get()), **self.BUTTON_STYLE)
        register_button.pack(**self.BUTTON_PACK)

    # Registers a new user
    def register_user(self, username, password):
        new_user_ID = generate_user_ID(self.connection)
        encrypted_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.userID = new_user_ID
        create_new_user(self.connection, new_user_ID, username, encrypted_password)
        self.show_user_ID()
        
    # Just displays the user's ID
    def show_user_ID(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        user_id_label = tk.Label(menu_frame, text=f"This is your user ID! \nWrite this down so you can log back in!\n{self.userID}", **self.LABEL_STYLE)
        user_id_label.pack(**self.LABEL_PACK)
        ok_button = tk.Button(menu_frame, text="Ok!", command=self.main_menu, **self.BUTTON_STYLE)
        ok_button.pack(**self.BUTTON_PACK)

    # Overall main menu
    def main_menu(self):
        # Reset is_host
        self.is_host = False
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        undercooked_title = tk.Label(menu_frame, text="Welcome to Undercooked!!!", **self.TITLE_STYLE)
        undercooked_title.pack(**self.TITLE_PACK)
        create_room_button = tk.Button(menu_frame, text="Create Room", command=self.create_room_menu, **self.BUTTON_STYLE)
        create_room_button.pack(**self.BUTTON_PACK)
        join_room_button = tk.Button(menu_frame, text="Join Room", command=self.join_room_menu, **self.BUTTON_STYLE)
        join_room_button.pack(**self.BUTTON_PACK)
        IP_address_button = tk.Button(menu_frame, text="Show IP Address", command=self.show_IP, **self.BUTTON_STYLE)
        IP_address_button.pack(**self.BUTTON_PACK)
        database_editor_button = tk.Button(menu_frame, text="Database Editor", command=self.database_editor_main_menu, **self.BUTTON_STYLE)
        database_editor_button.pack(**self.BUTTON_PACK)
        quit_button = tk.Button(menu_frame, text="Quit", command=self.quit_game, **self.BUTTON_STYLE)
        quit_button.pack(**self.BUTTON_PACK)

    # Popup that shows the user's IP address and port
    def show_IP(self):
        ip_addr = get_local_ip()
        IP_popup = messagebox.showinfo(self.root, message=ip_addr)

    # Ends the program
    def quit_game(self):
        self.root.destroy()

    # GUI for creating a room
    def create_room_menu(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        new_room_label = tk.Label(menu_frame, text="Enter the name of the room", **self.LABEL_STYLE)
        new_room_label.pack(**self.LABEL_PACK)
        new_room_name_input = tk.Entry(menu_frame, **self.ENTRY_STYLE)
        new_room_name_input.pack(**self.LABEL_PACK)
        create_room_button = tk.Button(menu_frame, text="Create Room", command=lambda: self.create_room(new_room_name_input.get()), **self.BUTTON_STYLE)
        create_room_button.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.main_menu, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)

    # GUI for joining a room
    def join_room_menu(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        # room_IP_button = tk.Entry(self.root)
        # room_IP_button.pack()
        join_room_label = tk.Label(menu_frame, text="Join Room\nEnter the room ID to join. Make sure you're connected to the same network and database\n", **self.LABEL_STYLE)
        join_room_label.pack(**self.LABEL_PACK)
        room_ID_button = tk.Entry(menu_frame, **self.ENTRY_STYLE)
        room_ID_button.pack(**self.LABEL_PACK)
        join_room_button = tk.Button(menu_frame, text="Join Room", command=lambda: self.join_room(room_ID_button.get()), **self.BUTTON_STYLE)
        join_room_button.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.main_menu, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)

    # Creates the room in the database
    def create_room(self, room_name):
        # Set is_host to true
        self.is_host = True
        new_room_id = generate_room_ID(self.connection)
        self.room_ID = new_room_id
        self.room_name = room_name
        create_new_room(self.connection, new_room_id, room_name)
        if (connect_to_room(self.connection, new_room_id, self.userID)):
            self.waiting_room_host()
        else:
            messagebox.showerror(message="Room not found")
            self.main_menu()

    # Logic for joining an established room
    def join_room(self, room_ID):
        if (connect_to_room(self.connection, room_ID, self.userID)):
            self.room_ID = room_ID
            self.is_host = False
            self.room_name = get_room_name_from_ID(self.connection, self.room_ID) # The function
            self.waiting_room_guest()
        else:
            messagebox.showerror(message="Room not found")
            self.main_menu()

    # The actual waiting room before the game starts for the host
    def waiting_room_host(self):
        self.clear_screen()
        # Sets logged in status
        set_log_in(self.connection, True, self.userID)
        # Retrieves names of all players
        current_players_list = tk.StringVar()
        current_players_list.set(setup_for_stringvar(get_all_players(self.connection, self.room_ID)))

        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        room_name_label = tk.Label(menu_frame, text=self.room_name, **self.TITLE_STYLE)
        room_name_label.pack(**self.TITLE_PACK)
        room_ID_label = tk.Label(menu_frame, text="Room ID: " + str(self.room_ID), **self.LABEL_STYLE)
        room_ID_label.pack(**self.LABEL_PACK)
        IP_address_button = tk.Button(menu_frame, text="Show IP Address", command=self.show_IP, **self.BUTTON_STYLE)
        IP_address_button.pack(**self.BUTTON_PACK)
        players_list = tk.Label(menu_frame, textvariable=current_players_list, **self.PANEL_STYLE)
        players_list.pack(**self.LABEL_PACK)
        update_players_list_button = tk.Button(menu_frame, text="Refresh Player List", command=lambda: [current_players_list.set(setup_for_stringvar(get_all_players(self.connection, self.room_ID))), self.waiting_room_host()], **self.BUTTON_STYLE)
        update_players_list_button.pack(**self.BUTTON_PACK)
        start_button = tk.Button(menu_frame, text="Start Game", command=self.start_day, **self.BUTTON_STYLE)
        start_button.pack(**self.BUTTON_PACK)
    
    # Starts the game (database setup from the host)
    def start_day(self):
        increment_day(self.connection, self.room_ID)
        self.restaurant_obj = Restaurant(self.room_name, self.room_ID, self.connection)
        self.restaurant_obj.update_restaurant()
        self.restaurant_obj.create_customers(self.num_players)
        set_time(self.connection, int(time.time()) + self.TIME_CONSTRAINT_SECONDS, self.room_ID)
        messagebox.showinfo(message="The game has begun!")
        self.restaurant_menu()

    # This is where the guests wait
    def waiting_room_guest(self):
        self.clear_screen()
        
        # Sets logged in status
        set_log_in(self.connection, True, self.userID)
        
        # Retrieves names of all players
        current_players_list = tk.StringVar()
        current_players_list.set(setup_for_stringvar(get_all_players(self.connection, self.room_ID)))
        
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        room_name_label = tk.Label(menu_frame, text=self.room_name, **self.TITLE_STYLE)
        room_name_label.pack(**self.TITLE_PACK)
        room_ID_label = tk.Label(menu_frame, text="Room ID: " + str(self.room_ID), **self.LABEL_STYLE)
        room_ID_label.pack(**self.LABEL_PACK)
        IP_address_button = tk.Button(menu_frame, text="Show IP Address", command=self.show_IP, **self.BUTTON_STYLE)
        IP_address_button.pack(**self.BUTTON_PACK)
        waiting_button = tk.Label(menu_frame, text="Waiting for host to start game", **self.LABEL_STYLE)
        waiting_button.pack(**self.LABEL_PACK)
        players_list = tk.Label(menu_frame, textvariable=current_players_list, **self.PANEL_STYLE)
        players_list.pack(**self.LABEL_PACK)
        update_players_list_button = tk.Button(menu_frame, text="Refresh Player List", command= lambda: current_players_list.set(setup_for_stringvar(get_all_players(self.connection, self.room_ID))), **self.BUTTON_STYLE)
        update_players_list_button.pack(**self.BUTTON_PACK)
        join_game_button = tk.Button(menu_frame, text="Join Game", command=self.has_game_started, **self.BUTTON_STYLE)
        join_game_button.pack(**self.BUTTON_PACK)
        #Show all other players in the room, room ID, and room name
    
    #Function for determining if players can actually join the game
    def has_game_started(self):
        day_num: int = check_day(self.connection, self.room_ID)
        if day_num > 0:
            messagebox.showinfo(message="You have successfully joined the game!")
            # Creates restaurant object
            self.restaurant_obj = Restaurant(self.room_name, self.room_ID, self.connection)
            self.restaurant_obj.update_restaurant()
            self.restaurant_menu()
        else:
            messagebox.showerror(message="The game hasn't started yet. You will be able to join when the host starts the game")
            self.waiting_room_guest()
            
    # This is the menu that first opens when the game starts
    def restaurant_menu(self):
        day_over = check_day_end(self.connection, self.room_ID, len(self.restaurant_obj.customers))
        if day_over == True:
            messagebox.showinfo(message="The day is over!")
            self.next_day()
        else:
            self.restaurant_obj.update_restaurant()
            self.clear_screen()
            self.player = Entity(get_username(self.connection, self.userID), self.connection, True)
            self.player.health = self.player.max_health
            menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
            menu_frame.pack(expand=True)
            cook_button = tk.Button(menu_frame, text="Cook", command=self.cook_menu, **self.BUTTON_STYLE)
            cook_button.pack(**self.BUTTON_PACK)
            equipment_button = tk.Button(menu_frame, text="Equipment", command=self.equipment_menu, **self.BUTTON_STYLE)
            equipment_button.pack(**self.BUTTON_PACK)
            shop_button = tk.Button(menu_frame, text="Shop", command=self.shop_menu, **self.BUTTON_STYLE)
            shop_button.pack(**self.BUTTON_PACK)
            status_button = tk.Button(menu_frame, text="Check Restaurant Status", command=self.restaurant_status, **self.BUTTON_STYLE)
            status_button.pack(**self.BUTTON_PACK)
            rpg_switch_button = tk.Button(menu_frame, text="To the Wilderness", command=self.wilderness_area_select, **self.BUTTON_STYLE)
            rpg_switch_button.pack(**self.BUTTON_PACK)
            quit_button = tk.Button(menu_frame, text="Quit", command=self.quit_game, **self.BUTTON_STYLE)
            quit_button.pack(**self.BUTTON_PACK)

    # This is the menu that opens to let the player choose which area they are going to
    def wilderness_area_select(self):
        selected_area = tk.StringVar(self.root)
        selected_area.set("Select an Area")
        unlocked_areas_list = get_area_names(self.connection, self.room_ID)
        select_checkbox = tk.BooleanVar(self.root)
        self.clear_screen()
        
        ingredients_forecast = tk.StringVar()
        ingredients_forecast.set(setup_ingredients_forecast(selected_area.get(), self.connection))
        # Sets up frame for the ingredient forecast
        ingredients_forecast_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        ingredients_forecast_frame.pack(side="right", padx=self.PAD_X, pady=self.PAD_Y)
        ingredients_forecast_box = tk.Label(ingredients_forecast_frame, textvariable=ingredients_forecast, **self.PANEL_STYLE)
        ingredients_forecast_box.pack(fill="both")
        
        # Centered frame that holds the area selection widgets
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)

        wilderness_title = tk.Label(menu_frame, text="Welcome to the Wilderness!\nSelect an Area!", **self.TITLE_STYLE)
        wilderness_title.pack(**self.TITLE_PACK)
        areas_dropdown = tk.OptionMenu(menu_frame, selected_area, *unlocked_areas_list) 
        # Styles the dropdown button and its popup list
        areas_dropdown.config(**self.OPTIONMENU_STYLE)
        areas_dropdown["menu"].config(font=self.BODY_FONT)
        areas_dropdown.pack(**self.LABEL_PACK)
        show_forecast_button = tk.Button(menu_frame, text="Show area ingredient forecast", command= lambda: ingredients_forecast.set(setup_ingredients_forecast(selected_area.get(), self.connection)), **self.BUTTON_STYLE)
        show_forecast_button.pack(**self.BUTTON_PACK)
        checkpoint_checkbox = tk.Checkbutton(menu_frame, text="Start From Checkpoint?", variable=select_checkbox, onvalue=True, offvalue=False, **self.CHECKBUTTON_STYLE)
        checkpoint_checkbox.pack(**self.LABEL_PACK)
        go_to_wilderness = tk.Button(menu_frame, text="Go!", command= lambda: self.check_area_select(selected_area.get(), select_checkbox.get()), **self.BUTTON_STYLE)
        go_to_wilderness.pack(**self.BUTTON_PACK)
        
    # Validates the information provided in wilderness_area_select and selects next menu based on it
    def check_area_select(self, selected_area_name: str, checkpoint_bool: bool) -> None:
        checkpoint_exists: bool = False
        everything_valid: bool = False
        area_message = "You enter " + selected_area_name
        checkpoint_num: int = look_for_checkpoint(selected_area_name, self.checkpoints)
        
        if checkpoint_num != 0:
            checkpoint_exists = True

        #Checks if area was selected. If not, rerun menu
        if selected_area_name == "Select an Area":
            messagebox.showinfo(self.root, message="Please select an area")
            self.wilderness_area_select()
        # If no checkpoint selected (starting from beginning) AND area selected, run next menu
        elif checkpoint_bool == False:
            everything_valid = True
        # If Area is valid and the user tries to start from a checkpoint, check to see if they have a checkpoint
        else:
            if checkpoint_exists == False:
                messagebox.showinfo(self.root, message="You don't have a checkpoint at that location!")
                self.wilderness_area_select()
            else:
                area_message += " at node " + str(checkpoint_num)
                everything_valid = True
        # If checkpoint and area are good, continue
        if everything_valid == True:
            messagebox.showinfo(self.root, message=area_message)
            self.current_area = Area(selected_area_name, self.connection)
            # Sets checkpoint if there is one
            if self.current_area.current_node != checkpoint_num:
                self.current_area.current_node = checkpoint_num
            # Calls the iterative node function
            self.explore_node()

    # This function overall handles nodes. It acts like a loop
    # This function specifically has the menu for campsites and checkpoints
    # This series of functions is kind of like Assembly labels due to how TKinter works. 
    def explore_node(self, pause_zone = False):
        # Checks for the end of the day. If so, drop half of your gathered ingredients
        day_over = check_day_end(self.connection, self.room_ID, len(self.restaurant_obj.customers))
        if day_over == True:
            messagebox.showinfo(message="The day is over!\nAs you hurry back to the restaurant before nightfall, you drop half of your gathered ingredients! Oh no!")
            self.local_inventory = drop_random_ingredients(self.local_inventory)
            inv_to_database(self.connection, self.room_ID, self.local_inventory)
            self.next_day()
        else:
            self.clear_screen()
            # Resets the combat log
            self.combat_log = []
            # Stays at same location when checkpoint is enabled
            if pause_zone == False:
                self.current_area.current_node = self.current_area.current_node + 1
            # Kick back to the restaurant when done
            if self.current_area.progress == False:
                self.restaurant_menu()

            #Every time you load into a node, check for a campsite or checkpoint (5 and 10 respectively)
            #Campsite logic
            if self.current_area.current_node % 5 == 0:
                menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
                menu_frame.pack(expand=True)
                campsite_label = tk.Label(menu_frame, text="Welcome to the campsite\nPick one of the following", **self.TITLE_STYLE)
                campsite_label.pack(**self.TITLE_PACK)
                check_status_button = tk.Button(menu_frame, text="Check Status", command=self.check_player_status, **self.BUTTON_STYLE)
                check_status_button.pack(**self.BUTTON_PACK)
                full_heal_button = tk.Button(menu_frame, text="Full Heal", command=self.full_heal_menu, **self.BUTTON_STYLE)
                full_heal_button.pack(**self.BUTTON_PACK)
                return_inventory_button = tk.Button(menu_frame, text="Return ingredients to restaurant and heal 25% of your health", command=self.half_and_half, **self.BUTTON_STYLE)
                return_inventory_button.pack(**self.BUTTON_PACK)
                return_to_restaurant_button = tk.Button(menu_frame, text="Return to the restaurant", command=lambda: [inv_to_database(self.connection, self.room_ID, self.local_inventory), self.restaurant_menu()], **self.BUTTON_STYLE)
                return_to_restaurant_button.pack(**self.BUTTON_PACK)
                #Checkpoint additional logic
                if self.current_area.current_node % 10 == 0:
                    set_checkpoint_button = tk.Button(menu_frame, text="Set a checkpoint", command=self.set_checkpoint, **self.BUTTON_STYLE)
                    set_checkpoint_button.pack(**self.BUTTON_PACK)
            # Generate a normal node
            else:
                # Handles node generation and sets appropriate flags
                self.current_area.generate_node()
                #Triggers text for the type of node
                self.node_type_text()
    
    # Displays the player's status, inventory, current node, and area checkpoint
    def check_player_status(self):
        self.clear_screen()
        player_status = tk.StringVar()
        player_status.set(setup_for_stringvar(output_entity_stats(self.player, True)))
        
        ingredients_inventory = tk.StringVar()
        ingredients_inventory.set(print_ingredients(self.local_inventory))
        
        # Bottom frame is packed first so the button stays visible if the content is long
        bottom_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        bottom_frame.pack(side="bottom", fill="x", pady=self.PAD_Y)
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        
        player_status_label = tk.Label(menu_frame, textvariable=player_status, **self.PANEL_STYLE)
        player_status_label.pack(**self.LABEL_PACK)
        ingredients_inventory_display = tk.Label(menu_frame, textvariable=ingredients_inventory, **self.PANEL_STYLE)
        ingredients_inventory_display.pack(**self.LABEL_PACK)
        current_zone = tk.Label(menu_frame, text=f"Current Node: {self.current_area.current_node}", **self.LABEL_STYLE)
        current_zone.pack(**self.LABEL_PACK)
        current_area_checkpoint = tk.Label(menu_frame, text=f"Current Checkpoint: Node {self.get_checkpoint()}", **self.LABEL_STYLE)
        current_area_checkpoint.pack(**self.LABEL_PACK)
        ok_button = tk.Button(bottom_frame, text="Continue", command=lambda: self.explore_node(True), **self.BUTTON_STYLE)
        ok_button.pack(**self.BUTTON_PACK)
    
    # Sets a checkpoint for an area
    def set_checkpoint(self):
        checkpoint_message = "Your checkpoint has been set at node "
        # Regardless of whether or not the checkpoint exists, it is added or updated
        self.checkpoints[self.current_area.name] = self.current_area.current_node
        messagebox.showinfo(self.root, message=checkpoint_message+str(self.current_area.current_node))
        self.explore_node(True)
    
    # Removes a checkpoint
    def remove_checkpoint(self):
        try:
            checkpoint_message: str = "Your checkpoint has been removed in " + self.current_area.name
            self.checkpoints.pop(self.current_area.name)
        except KeyError:
            checkpoint_message = "You don't have a checkpoint in " + self.current_area.name
        messagebox.showinfo(self.root, checkpoint_message)   

    # Full heal from campfire
    def full_heal_menu(self):
        self.player.health = self.player.max_health
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        text_label = tk.Label(menu_frame, text="You heal to full health", **self.LABEL_STYLE)
        text_label.pack(**self.LABEL_PACK)
        ok_button = tk.Button(menu_frame, text="Ok", command=self.explore_node, **self.BUTTON_STYLE)
        ok_button.pack(**self.BUTTON_PACK)

    # Heal 25% health and return inventory to restaurant
    def half_and_half(self):
        self.clear_screen()
        # Sends off your inventory to the database
        inv_to_database(self.connection, self.room_ID, self.local_inventory)
        self.local_inventory = []
        self.player.health += round(self.player.max_health * .25)
        # Don't allow for going over max health
        if self.player.health > self.player.max_health:
            self.player.health = self.player.max_health
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        text_label = tk.Label(menu_frame, text="You heal 25% of your health and send your inventory back to the restaurant", **self.LABEL_STYLE)
        text_label.pack(**self.LABEL_PACK)
        ok_button = tk.Button(menu_frame, text="Ok", command=self.explore_node, **self.BUTTON_STYLE)
        ok_button.pack(**self.BUTTON_PACK)

    # Node type text
    def node_type_text(self):
        self.clear_screen()
        # Sets flavor message for popup to signify node type
        # NOTE: Maybe do random messages of each type to add a little more flavor
        if self.current_area.node_type == "fishing":
            node_type_message = "This looks like a great spot to go FISHING!"
        elif self.current_area.node_type == "flora":
            node_type_message = "It looks like you could harvest some delicious PLANTS around here"
        elif self.current_area.node_type == "fauna":
            node_type_message = "One might say this would be a great spot to go HUNTING"
        
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        gather_label = tk.Label(menu_frame, text=node_type_message, **self.LABEL_STYLE)
        gather_label.pack(**self.LABEL_PACK)
        ok_button = tk.Button(menu_frame, text="Ok", command=self.is_there_an_enemy, **self.BUTTON_STYLE)
        ok_button.pack(**self.BUTTON_PACK)

    # Checks to see if a newly generated node has an enemy
    def is_there_an_enemy(self):
        if self.current_area.is_enemy == True:
            self.enemy_node_text()
        else:
            self.harvest_node_text()

    # Shows text for nodes with enemy
    def enemy_node_text(self):
        self.clear_screen()
        self.current_enemy = Entity(self.current_area.enemy_name, self.connection)
        # Change flavor text for elite or not
        if self.current_area.is_elite == True:
            enemy_message = "You encounter a " + self.current_area.enemy_name + "\nIt looks incredibly strong!\n"
            # Scaling up everything except for damage
            self.current_enemy.max_health *= self.current_enemy.ELITE_ENEMY_HEALTH_SCALAR
            self.current_enemy.health *= self.current_enemy.ELITE_ENEMY_HEALTH_SCALAR
            self.current_enemy.defense *= self.current_enemy.ELITE_ENEMY_DEFENSE_SCALAR
            # Sets Entity attribute for being elite as well
            self.current_enemy.is_elite = True
        else:
            enemy_message = "While observing the landscape, a " + self.current_area.enemy_name + " appears!\n"
            # self.current_enemy
        
        # Triggers an additional message for a boss encounter. A boss can be elite
        if self.current_enemy.is_boss == True:
            enemy_message += "This foe appears to be especially mighty. It must be a BOSS!"
            self.current_area.is_boss = True
        
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        text_label = tk.Label(menu_frame, text=enemy_message, **self.LABEL_STYLE)
        text_label.pack(**self.LABEL_PACK)
        ok_button = tk.Button(menu_frame, text="Ok", command=self.battle_menu, **self.BUTTON_STYLE)
        ok_button.pack(**self.BUTTON_PACK)

    # Text for harvesting the node
    def harvest_node_text(self):
        self.clear_screen()
        node_ingredients: list[str] = []
        # If player falls, skip this function
        # if self.player.health <= 0:
        #     self.fallen_text()

        # Add ingredient to your inventory
        node_ingredients.append(harvest_item(self.current_area.chosen_list, self.local_inventory))
        
        # If enemy was elite, get a second roll
        if self.current_area.is_elite:
            node_ingredients.append(harvest_item(self.current_area.chosen_list, self.local_inventory))

        # If enemy was a boss, get an additional 2 rolls
        if self.current_area.is_boss:
            node_ingredients.append(harvest_item(self.current_area.chosen_list, self.local_inventory))
            node_ingredients.append(harvest_item(self.current_area.chosen_list, self.local_inventory))

            
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        text_label = tk.Label(menu_frame, text=f"You harvested: \n{setup_for_stringvar(node_ingredients)}", **self.LABEL_STYLE)
        text_label.pack(**self.LABEL_PACK)
        ok_button = tk.Button(menu_frame, text="Ok", command=self.explore_node, **self.BUTTON_STYLE)
        ok_button.pack(**self.BUTTON_PACK)

    # Text for if the character falls
    def fallen_text(self):
        self.clear_screen()
        # Removes the checkpoint in the area
        if self.get_checkpoint() != 0:
            self.remove_checkpoint()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        gather_label = tk.Label(menu_frame, text="You run back to the restaurant injured, dropping all of your ingredients along the way", **self.LABEL_STYLE)
        gather_label.pack(**self.LABEL_PACK)
        ok_button = tk.Button(menu_frame, text="Ok", command=self.restaurant_menu, **self.BUTTON_STYLE)
        ok_button.pack(**self.BUTTON_PACK)

    # This displays the GUI for the combat
    def battle_menu(self):
        self.clear_screen()
        # if (self.player.health <= 0):
        #     self.harvest_node_text()
        
        #TKinter variable setups
        local_combat_log = tk.StringVar()
        local_combat_log.set(setup_for_stringvar(self.combat_log))
        self.combat_log = []
        
        local_player_stats = tk.StringVar()
        local_player_stats.set(setup_for_stringvar(output_entity_stats(self.player)))
        
        local_enemy_stats = tk.StringVar()
        local_enemy_stats.set(setup_for_stringvar(output_entity_stats(self.current_enemy)))
        
        # Frames
        stats_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        stats_frame.pack(side="left", fill="both", expand=True, padx=self.PAD_X, pady=self.PAD_Y)
        combat_log_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        combat_log_frame.pack(side="right", fill="both", expand=True, padx=self.PAD_X, pady=self.PAD_Y)
        combat_buttons_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        combat_buttons_frame.pack(side="bottom", pady=self.PAD_Y)
        # combat_buttons_frame.pack(side="bottom")
        
        # Displays
        player_stats_screen = tk.Label(stats_frame, textvariable=local_player_stats, **self.PANEL_STYLE)
        player_stats_screen.pack(fill="both", **self.LABEL_PACK)
        enemy_stats_screen = tk.Label(stats_frame, textvariable=local_enemy_stats, **self.PANEL_STYLE)
        enemy_stats_screen.pack(fill="both", **self.LABEL_PACK)
        combat_log_menu = tk.Label(combat_log_frame, textvariable=local_combat_log, **self.PANEL_STYLE)
        combat_log_menu.pack(fill="both", **self.LABEL_PACK)
        
        # Button Menu
        attack_button = tk.Button(combat_buttons_frame, text="Attack", command=self.wrapper_attack, **self.BUTTON_STYLE)
        attack_button.pack(fill="both", side="left", **self.BUTTON_PACK)
        
        parry_button = tk.Button(combat_buttons_frame, text="Parry", command=self.wrapper_parry, **self.BUTTON_STYLE)
        parry_button.pack(fill="both", side="left", **self.BUTTON_PACK)
        
        guard_button = tk.Button(combat_buttons_frame, text="Guard", command=self.wrapper_guard, **self.BUTTON_STYLE)
        guard_button.pack(fill="both", side="left", **self.BUTTON_PACK)
        
        flee_button = tk.Button(combat_buttons_frame, text="Flee(Cowardly)", command=self.wrapper_flee, **self.BUTTON_STYLE)
        flee_button.pack(fill="both", side="left", **self.BUTTON_PACK)
    
    # Wrapper function for attack
    def wrapper_attack(self):
        self.clear_screen()
        combat_attack(self.player, self.current_enemy, self.combat_log)
        combat_enemy_attack(self.player, self.current_enemy, log_list=self.combat_log)
        self.is_player_alive()
    
    # Wrapper function for parry
    def wrapper_parry(self):
        self.clear_screen()
        dodge_value = combat_parry_counter(self.player, self.current_enemy, self.combat_log)
        combat_enemy_attack(self.player, self.current_enemy, 0, dodge_value, self.combat_log)
        self.is_player_alive()
        
    # Wrapper function for guarding
    def wrapper_guard(self):
        self.clear_screen()
        guard_value = combat_defend(self.player, self.combat_log)
        combat_enemy_attack(self.player, self.current_enemy, guard_value, log_list=self.combat_log)
        self.is_player_alive()
        
    # Wrapper function for handling fleeing
    def wrapper_flee(self):
        successful_flee: bool = combat_flee(self.player, self.current_enemy, self.combat_log)
        if successful_flee == True: 
            # Drops half of your inventory
            self.local_inventory = drop_random_ingredients(self.local_inventory)
            # Uncomment when Ingredients JSON is ready
            # inv_to_database(connection, self.room_ID, self.local_inventory)
            messagebox.showinfo(message=f"As you flee, you dropped half of your collected ingredients in your hurry. However, you kept: {print_ingredients(self.local_inventory)}\n")
            self.restaurant_menu()
        else: 
            combat_enemy_attack(self.player, self.current_enemy, log_list=self.combat_log)
            self.is_player_alive()
        
    # Checks if enemy is slain. If so, returns to harvest_node
    def is_enemy_slain(self):
        self.clear_screen()
        enemy_defeated_text = f"You have slain the {self.current_enemy.name}"
        if self.current_enemy.health <= 0:
            menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
            menu_frame.pack(expand=True)
            enemy_slain_label = tk.Label(menu_frame, text=enemy_defeated_text, **self.LABEL_STYLE)
            enemy_slain_label.pack(**self.LABEL_PACK)
            enemy_slain_ok = tk.Button(menu_frame, text="Ok!", command=self.harvest_node_text, **self.BUTTON_STYLE)
            enemy_slain_ok.pack(**self.BUTTON_PACK)
        else: 
            self.battle_menu()
    
    # Checks for if the player is still alive
    def is_player_alive(self):
        if self.player.health > 0:
            self.is_enemy_slain()
        else:
            self.fallen_text()
        
    # Retrieves checkpoint
    def get_checkpoint(self) -> int:
        checkpoint_num = 0
        try:
            checkpoint_num = self.checkpoints[self.current_area.name]
        except KeyError:
            checkpoint_num = 0
        return checkpoint_num
    
    # The menu for interacting with cooking and fulfilling orders of customers
    def cook_menu(self):
        self.clear_screen()
        # Updates everything for the restaurant
        self.restaurant_obj.update_restaurant()
        # Sets up for displaying ingredients in inventory
        ingredients_list = print_ingredients_full(self.restaurant_obj.access_database_inventory_filter_type_id(1))
        
        # Frames
        orders_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        orders_frame.pack(side=tk.LEFT, expand=True, fill="both", padx=self.PAD_X, pady=self.PAD_Y)
        
        ingredients_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        ingredients_frame.pack(side=tk.RIGHT, expand=True, fill="both", padx=self.PAD_X, pady=self.PAD_Y)
        
        buttons_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        buttons_frame.pack(side=tk.BOTTOM, pady=self.PAD_Y)
        
        # Orders GUI (frame holds the listbox and its scrollbar)
        orders_list_frame = tk.Frame(orders_frame, **self.FRAME_STYLE)
        orders_list_frame.pack(expand=True, **self.LABEL_PACK)
        orders_scrollbar = tk.Scrollbar(orders_list_frame)
        orders_scrollbar.pack(side="right", fill="y")
        orders_interface = tk.Listbox(orders_list_frame, selectmode=tk.SINGLE, yscrollcommand=orders_scrollbar.set, width=self.LISTBOX_WIDTH, height=self.LISTBOX_HEIGHT, **self.LISTBOX_STYLE)
        # Write a query to bring down the names of the requested orders
        orders_interface.insert(0, *self.restaurant_obj.display_customer_order_list())
        orders_interface.pack(side="left", fill="both", expand=True)
        orders_scrollbar.config(command=orders_interface.yview)
        
        # Ingredients Inventory GUI
        ingredients_display = tk.Label(ingredients_frame, text=f"{ingredients_list}", **self.PANEL_STYLE) 
        ingredients_display.pack(side="top", expand=True, **self.LABEL_PACK)
        
        # Buttons GUI
        back_button = tk.Button(buttons_frame, text="Back", command=self.restaurant_menu, **self.BUTTON_STYLE)
        back_button.pack(side=tk.LEFT, **self.BUTTON_PACK)
        
        # Refreshes the page
        refresh_button = tk.Button(buttons_frame, text="Refresh", command=self.cook_menu, **self.BUTTON_STYLE)
        refresh_button.pack(side=tk.LEFT, **self.BUTTON_PACK)
        cook_button = tk.Button(buttons_frame, text="Cook selected order meal", command=lambda: self.cook_order(orders_interface.curselection()[0]), **self.BUTTON_STYLE)
        cook_button.pack(side=tk.LEFT, **self.BUTTON_PACK)
    
    # Function that actually handles cooking an order
    def cook_order(self, selected_order_index):
        if selected_order_index == None:
            messagebox.showwarning(message="You haven't select an order!")
            self.cook_menu()
        else:
            self.clear_screen()
            current_customer: Customer = self.restaurant_obj.customers[selected_order_index]
            customer_order: Recipe = current_customer.order
            ingredients_list: list[tuple[int, int, int]] = []
            if current_customer.still_exist() == True:
                # Setup to send this data in remove item
                # Iterates through each type of item
                for i in range(len(customer_order.raw_ingredients)):
                    temp_type_id = 1
                    temp_ingredient_id: int = int(customer_order.raw_ingredients[i][0])
                    temp_ingredient_quantity: int = int(customer_order.raw_ingredients[i][1])
                    temp_tuple = (temp_type_id, temp_ingredient_id, temp_ingredient_quantity)
                    ingredients_list.append(temp_tuple)
                    
                # Checks if this order can be cooked based on the user's ingredients
                successful_cook = self.restaurant_obj.remove_item(ingredients_list)
                if successful_cook != True:
                    messagebox.showerror(message="Check your supply, chef. You don't have the necessary ingredients to cook that!")
                    self.cook_menu()
                else:
                    current_customer.delete()
                    self.restaurant_obj.update_restaurant()
                    messagebox.showinfo(message="Order fulfilled!")
                    self.cook_menu()
            else:
                messagebox.showerror(message="That customer's order has already been fulfilled!")
                self.cook_menu()
            
    # Allows for equipping weapons and armor
    def equipment_menu(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        equipment_label = tk.Label(menu_frame, text="Equip yourself!", **self.TITLE_STYLE)
        equipment_label.pack(**self.TITLE_PACK)
        weapon_equip = tk.Button(menu_frame, text="Weapons", command=self.weapon_select_menu, **self.BUTTON_STYLE)
        weapon_equip.pack(**self.BUTTON_PACK)
        armor_equip = tk.Button(menu_frame, text="Armor", command=self.armor_select_menu, **self.BUTTON_STYLE)
        armor_equip.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.restaurant_menu, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
        
    # Menu for equipping a weapon
    def weapon_select_menu(self):
        inventory_weapons_list: list[str] =  []
        weapon_stats = tk.StringVar()
        weapon_stats.set("No weapon selected to inspect")
        
        # Sets display string for current weapon
        current_weapon_stats = tk.StringVar()
        current_weapon_stats.set(self.weapon.display())
        
        self.clear_screen()
        # Setting up frames (bottom is packed first so the buttons stay visible)
        bottom_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        bottom_frame.pack(side="bottom", fill="x", padx=self.PAD_X, pady=self.PAD_Y)
        left_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        left_frame.pack(side="left", fill="both", expand=True, padx=self.PAD_X, pady=self.PAD_Y)
        middle_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        middle_frame.pack(side="left", fill="both", expand=True, padx=self.PAD_X, pady=self.PAD_Y)
        right_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        right_frame.pack(side="left", fill="both", expand=True, padx=self.PAD_X, pady=self.PAD_Y)
        
        # Setting up menus
        weapons_inventory_label = tk.Label(left_frame, text="Weapons Inventory", **self.LABEL_STYLE)
        weapons_inventory_label.pack(**self.LABEL_PACK)
        # Frame holds the listbox and its scrollbar
        weapons_list_frame = tk.Frame(left_frame, **self.FRAME_STYLE)
        weapons_list_frame.pack(**self.LABEL_PACK)
        weapons_scrollbar = tk.Scrollbar(weapons_list_frame)
        weapons_scrollbar.pack(side="right", fill="y")
        weapons_inventory = tk.Listbox(weapons_list_frame, selectmode="single", yscrollcommand=weapons_scrollbar.set, width=self.LISTBOX_WIDTH, height=self.LISTBOX_HEIGHT, **self.LISTBOX_STYLE)
        weapons_inventory.pack(side="left", fill="both", expand=True)
        weapons_scrollbar.config(command=weapons_inventory.yview)
        # Should retrieve all weapon tuples and then filter them down into a list of their names for display
        database_inventory_tuples = self.restaurant_obj.access_database_inventory_filter_type_id(2)
        
        for inventory_tuple in database_inventory_tuples:
            inventory_weapons_list.append(inventory_tuple[2])
            
        weapons_inventory.insert(0, *inventory_weapons_list)
        
        selected_weapon_compare = tk.Label(middle_frame, textvariable=weapon_stats, **self.PANEL_STYLE)
        selected_weapon_compare.pack(fill="both", expand=True, **self.LABEL_PACK)
        
        # Sets what weapon's stats to show in the inspector menu
        inspect_weapon_button = tk.Button(bottom_frame, text="Inspect Selected Weapon", command=lambda: weapon_stats.set(Weapon(weapons_inventory.get(weapons_inventory.curselection())).display()), **self.BUTTON_STYLE)
        inspect_weapon_button.pack(side="left", expand=True, **self.BUTTON_PACK)
        
        current_weapon_display = tk.Label(right_frame, textvariable=current_weapon_stats, **self.PANEL_STYLE)
        current_weapon_display.pack(side="left", fill="both", expand=True, **self.LABEL_PACK)
        
        equip_weapon_button = tk.Button(bottom_frame, text="Equip", command=lambda: self.equip_weapon(weapons_inventory.get(weapons_inventory.curselection())), **self.BUTTON_STYLE)
        equip_weapon_button.pack(side="left", expand=True, **self.BUTTON_PACK)
        
        back_button = tk.Button(bottom_frame, text="Back", command=self.equipment_menu, **self.BUTTON_STYLE)
        back_button.pack(side="left", expand=True, **self.BUTTON_PACK)
        
    # Handles the logic for equipping the weapon
    def equip_weapon(self, weapon_name: str):
        # Adds now unequipped weapon to the inventory
        self.restaurant_obj.add_item([(self.weapon.type_id, self.weapon.item_id, self.weapon.name, 1)])
        self.clear_screen()
        # Equips new weapon and removes it from the inventory
        self.weapon = Weapon(weapon_name)
        self.restaurant_obj.remove_item([(self.weapon.type_id, self.weapon.item_id, 1)])
        messagebox.showinfo(message=f"You equip {self.weapon.name}!")
        self.weapon_select_menu()
        
    # Menu for equipping armor
    def armor_select_menu(self):
        inventory_armor_list: list[str] =  []
        armor_stats = tk.StringVar()
        armor_stats.set("No armor selected to inspect")
        
        # Sets display string for current armor
        current_armor_stats = tk.StringVar()
        current_armor_stats.set(self.armor.display())
        
        self.clear_screen()
        # Setting up frames (bottom is packed first so the buttons stay visible)
        bottom_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        bottom_frame.pack(side="bottom", fill="x", padx=self.PAD_X, pady=self.PAD_Y)
        left_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        left_frame.pack(side="left", fill="both", expand=True, padx=self.PAD_X, pady=self.PAD_Y)
        middle_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        middle_frame.pack(side="left", fill="both", expand=True, padx=self.PAD_X, pady=self.PAD_Y)
        right_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        right_frame.pack(side="left", fill="both", expand=True, padx=self.PAD_X, pady=self.PAD_Y)
        
        # Setting up menus
        armor_inventory_label = tk.Label(left_frame, text="Armors Inventory", **self.LABEL_STYLE)
        armor_inventory_label.pack(**self.LABEL_PACK)
        # Frame holds the listbox and its scrollbar
        armor_list_frame = tk.Frame(left_frame, **self.FRAME_STYLE)
        armor_list_frame.pack(**self.LABEL_PACK)
        armor_scrollbar = tk.Scrollbar(armor_list_frame)
        armor_scrollbar.pack(side="right", fill="y")
        armor_inventory = tk.Listbox(armor_list_frame, selectmode="single", yscrollcommand=armor_scrollbar.set, width=self.LISTBOX_WIDTH, height=self.LISTBOX_HEIGHT, **self.LISTBOX_STYLE)
        armor_inventory.pack(side="left", fill="both", expand=True)
        armor_scrollbar.config(command=armor_inventory.yview)
        # Should retrieve all weapon tuples and then filter them down into a list of their names for display
        database_inventory_tuples = self.restaurant_obj.access_database_inventory_filter_type_id(3)
        
        for inventory_tuple in database_inventory_tuples:
            inventory_armor_list.append(inventory_tuple[2])
            
        armor_inventory.insert(0, *inventory_armor_list)
        
        selected_armor_compare = tk.Label(middle_frame, textvariable=armor_stats, **self.PANEL_STYLE)
        selected_armor_compare.pack(fill="both", expand=True, **self.LABEL_PACK)
        
        # Sets what armor's stats to show in the inspector menu
        inspect_armor_button = tk.Button(bottom_frame, text="Inspect Selected Weapon", command=lambda: armor_stats.set(Armor(armor_inventory.get(armor_inventory.curselection())).display()), **self.BUTTON_STYLE)
        inspect_armor_button.pack(side="left", expand=True, **self.BUTTON_PACK)
        
        current_armor_display = tk.Label(right_frame, textvariable=current_armor_stats, **self.PANEL_STYLE)
        current_armor_display.pack(side="left", fill="both", expand=True, **self.LABEL_PACK)
        
        equip_armor_button = tk.Button(bottom_frame, text="Equip", command=lambda: self.equip_armor(armor_inventory.get(armor_inventory.curselection())), **self.BUTTON_STYLE)
        equip_armor_button.pack(side="left", expand=True, **self.BUTTON_PACK)
        
        back_button = tk.Button(bottom_frame, text="Back", command=self.equipment_menu, **self.BUTTON_STYLE)
        back_button.pack(side="left", expand=True, **self.BUTTON_PACK)
        
    # Handles the logic for equipping the armor
    def equip_armor(self, armor_name: str):
        # Adds now unequipped weapon to the inventory
        self.restaurant_obj.add_item([(self.armor.type_id, self.armor.item_id, self.armor.name, 1)])
        self.clear_screen()
        # Equips new armor and removes it from the inventory
        self.armor = Armor(armor_name)
        self.restaurant_obj.remove_item([(self.armor.type_id, self.armor.item_id, 1)])
        messagebox.showinfo(message=f"You equip {self.armor.name}!")
        self.armor_select_menu()
    
    # Displays the status of the restaurant
    def restaurant_status(self):
        self.clear_screen()
        self.restaurant_obj.update_restaurant()
        # Bottom frame is packed first so the button stays visible if the content is long
        bottom_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        bottom_frame.pack(side="bottom", fill="x", pady=self.PAD_Y)
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        restaurant_name_label = tk.Label(menu_frame, text=f"{self.restaurant_obj.restaurant_name}", **self.TITLE_STYLE)
        restaurant_name_label.pack(**self.TITLE_PACK)
        restaurant_money_label = tk.Label(menu_frame, text=f"Money: {self.restaurant_obj.money}", **self.LABEL_STYLE)
        restaurant_money_label.pack(**self.LABEL_PACK)
        day_label = tk.Label(menu_frame, text=f"Day: {self.restaurant_obj.day}", **self.LABEL_STYLE)
        day_label.pack(**self.LABEL_PACK)
        player_status_label = tk.Label(menu_frame, text="Your character's stats:\n", **self.LABEL_STYLE)
        player_status_label.pack(**self.LABEL_PACK)
        player_status = tk.StringVar()
        player_status.set(setup_for_stringvar(output_entity_stats(self.player, True)))
        # Frame places the weapon and armor panels side by side
        equipment_frame = tk.Frame(menu_frame, **self.FRAME_STYLE)
        equipment_frame.pack(**self.LABEL_PACK)
        weapon_info_display = tk.Label(equipment_frame, text=f"Equipment:\n\n{self.weapon.name}:\nAttack Roll: {transform_dice_to_str(self.weapon.attack_dice)}\n Average Damage: {dice_avg(self.weapon.attack_dice)}\nAttack Modifier: {self.weapon.modifier}\nPrice: {self.weapon.price}", **self.PANEL_STYLE)
        weapon_info_display.pack(side="left", fill="both", **self.LABEL_PACK)
        armor_info_display = tk.Label(equipment_frame, text=f"{self.armor.name}:\n Type: {self.armor.type}\nDefense: {self.armor.defense}\n Block Dice: {transform_dice_to_str(self.armor.block_dice)}\nDodge Dice: {transform_dice_to_str(self.armor.dodge_dice)}\nPrice: {self.armor.price}", **self.PANEL_STYLE)
        armor_info_display.pack(side="left", fill="both", **self.LABEL_PACK)
        ingredient_inventory_label = tk.Label(menu_frame, text=f"Ingredients Inventory: \n{print_ingredients_full(self.restaurant_obj.access_database_inventory_filter_type_id(1))}", **self.PANEL_STYLE)
        ingredient_inventory_label.pack(**self.LABEL_PACK)
        continue_button = tk.Button(bottom_frame, text="Back to work!", command=self.restaurant_menu, **self.BUTTON_STYLE)
        continue_button.pack(**self.BUTTON_PACK)

    #Overarching menu for the shop
    def shop_menu(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        weapons_shop_button = tk.Button(menu_frame, text="Weapons", command=self.weapons_shop, **self.BUTTON_STYLE)
        weapons_shop_button.pack(**self.BUTTON_PACK)
        armors_shop_button = tk.Button(menu_frame, text="Armor", command=self.armors_shop, **self.BUTTON_STYLE)
        armors_shop_button.pack(**self.BUTTON_PACK)
        cookbooks_shop_button = tk.Button(menu_frame, text="Cookbooks", command=self.cookbooks_shop, **self.BUTTON_STYLE)
        cookbooks_shop_button.pack(**self.BUTTON_PACK)
        quit_shop_button = tk.Button(menu_frame, text="Back", command=self.restaurant_menu, **self.BUTTON_STYLE)
        quit_shop_button.pack(**self.BUTTON_PACK)
        
    # Displays all weapons available for sale
    def weapons_shop(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        # Frame holds the listbox and its scrollbar
        weapons_list_frame = tk.Frame(menu_frame, **self.FRAME_STYLE)
        weapons_list_frame.pack(**self.LABEL_PACK)
        weapons_scrollbar = tk.Scrollbar(weapons_list_frame)
        weapons_scrollbar.pack(side="right", fill="y")
        weapons_display = tk.Listbox(weapons_list_frame, selectmode="single", yscrollcommand=weapons_scrollbar.set, width=self.LISTBOX_WIDTH, height=self.LISTBOX_HEIGHT, **self.LISTBOX_STYLE)
        weapons_display.pack(side="left", fill="both", expand=True)
        weapons_scrollbar.config(command=weapons_display.yview)
        weapons_array: list[str] = get_item_names("weapons")
        weapons_display.insert(0, *weapons_array)
        
        show_info_button = tk.Button(menu_frame, text="Inspect", command=lambda: self.display_weapon(weapons_display.get(weapons_display.curselection())), **self.BUTTON_STYLE)
        show_info_button.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.shop_menu, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
            
    # Shows information about the currently selected weapon
    def display_weapon(self, current_weapon: str):
        self.clear_screen()
        displayed_weapon: Weapon = Weapon(current_weapon)
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        weapon_info_display = tk.Label(menu_frame, text=f"{displayed_weapon.name}:\nAttack Roll: {transform_dice_to_str(displayed_weapon.attack_dice)}\n Average Damage: {dice_avg(displayed_weapon.attack_dice)}\nAttack Modifier: {displayed_weapon.modifier}\nPrice: {displayed_weapon.price}", **self.PANEL_STYLE)
        weapon_info_display.pack(**self.LABEL_PACK)
        show_money_label = tk.Label(menu_frame, text=f"You have {self.restaurant_obj.money} money left!", **self.LABEL_STYLE)
        show_money_label.pack(**self.LABEL_PACK)
        purchase_button = tk.Button(menu_frame, text="Purchase", command=lambda: self.weapon_purchase_wrapper(displayed_weapon), **self.BUTTON_STYLE)
        purchase_button.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.weapons_shop, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
        
    # Database logic for purchasing the weapon
    def weapon_purchase_wrapper(self, new_weapon: Weapon):
        # Check for money
        self.clear_screen()
        # Checks to see if you have money
        if self.restaurant_obj.money >= new_weapon.price:
            self.restaurant_obj.money -= new_weapon.price
            self.restaurant_obj.update_money()
            # Pushes item to local inventory and database inventory
            self.restaurant_obj.add_item([(new_weapon.type_id, new_weapon.item_id, new_weapon.name, 1)])
            menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
            menu_frame.pack(expand=True)
            weapon_purchase_confirmation = tk.Label(menu_frame, text=f"You bought {new_weapon.name} for {new_weapon.price}!\nYou have {self.restaurant_obj.money} money remaining", **self.LABEL_STYLE)
            weapon_purchase_confirmation.pack(**self.LABEL_PACK)
            ok_button = tk.Button(menu_frame, text="Yay!", command=self.shop_menu, **self.BUTTON_STYLE)
            ok_button.pack(**self.BUTTON_PACK)
        else:
            self.youre_broke()
        
    # Same as above but for armor
    def armors_shop(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        # Frame holds the listbox and its scrollbar
        armors_list_frame = tk.Frame(menu_frame, **self.FRAME_STYLE)
        armors_list_frame.pack(**self.LABEL_PACK)
        armors_scrollbar = tk.Scrollbar(armors_list_frame)
        armors_scrollbar.pack(side="right", fill="y")
        armors_display = tk.Listbox(armors_list_frame, selectmode="single", yscrollcommand=armors_scrollbar.set, width=self.LISTBOX_WIDTH, height=self.LISTBOX_HEIGHT, **self.LISTBOX_STYLE)
        armors_display.pack(side="left", fill="both", expand=True)
        armors_scrollbar.config(command=armors_display.yview)
        armors_array: list[str] = get_item_names("armors")
        armors_display.insert(0, *armors_array)
    
        show_info_button = tk.Button(menu_frame, text="Inspect", command=lambda: self.display_armor(armors_display.get(armors_display.curselection())), **self.BUTTON_STYLE)
        show_info_button.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.shop_menu, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
    
    def display_armor(self, current_armor: str):
        self.clear_screen()
        displayed_armor: Armor = Armor(current_armor)
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        armor_info_display = tk.Label(menu_frame, text=f"{displayed_armor.name}:\n Type: {displayed_armor.type}\nDefense: {displayed_armor.defense}\n Block Dice: {transform_dice_to_str(displayed_armor.block_dice)}\nDodge Dice: {transform_dice_to_str(displayed_armor.dodge_dice)}\nPrice: {displayed_armor.price}", **self.PANEL_STYLE)
        armor_info_display.pack(**self.LABEL_PACK)
        show_money_label = tk.Label(menu_frame, text=f"You have {self.restaurant_obj.money} money left!", **self.LABEL_STYLE)
        show_money_label.pack(**self.LABEL_PACK)
        purchase_button = tk.Button(menu_frame, text="Purchase", command=lambda: self.armor_purchase_wrapper(displayed_armor), **self.BUTTON_STYLE)
        purchase_button.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.armors_shop, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
        
    def armor_purchase_wrapper(self, new_armor: Armor):
        self.clear_screen()
        if self.restaurant_obj.money >= new_armor.price:
            self.restaurant_obj.money -= new_armor.price
            self.restaurant_obj.update_money()
            # Pushes item to local inventory and database inventory
            self.restaurant_obj.add_item([(new_armor.type_id, new_armor.item_id, new_armor.name, 1)])
            menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
            menu_frame.pack(expand=True)
            armor_purchase_confirmation = tk.Label(menu_frame, text=f"You bought {new_armor.name} for {new_armor.price}!\nYou have {self.restaurant_obj.money} money remaining", **self.LABEL_STYLE)
            armor_purchase_confirmation.pack(**self.LABEL_PACK)
            ok_button = tk.Button(menu_frame, text="Yay!", command=self.shop_menu, **self.BUTTON_STYLE)
            ok_button.pack(**self.BUTTON_PACK)
        else:
            self.youre_broke()
    
    # This one is a bit different
    def cookbooks_shop(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        # Frame holds the listbox and its scrollbar
        cookbooks_list_frame = tk.Frame(menu_frame, **self.FRAME_STYLE)
        cookbooks_list_frame.pack(**self.LABEL_PACK)
        cookbooks_scrollbar = tk.Scrollbar(cookbooks_list_frame)
        cookbooks_scrollbar.pack(side="right", fill="y")
        cookbooks_display = tk.Listbox(cookbooks_list_frame, selectmode="single", yscrollcommand=cookbooks_scrollbar.set, width=self.LISTBOX_WIDTH, height=self.LISTBOX_HEIGHT, **self.LISTBOX_STYLE)
        cookbooks_display.pack(side="left", fill="both", expand=True)
        cookbooks_scrollbar.config(command=cookbooks_display.yview)
        local_cookbooks_array: list[str] = get_cookbook_names(self.connection)
        #Removes already purchased cookbooks from display
        for purchased_cookbook in self.restaurant_obj.onetime_purchases:
            local_cookbooks_array.remove(purchased_cookbook)
            
        cookbooks_display.insert(0, *local_cookbooks_array)
        
        show_info_button = tk.Button(menu_frame, text="Inspect", command=lambda: self.display_cookbook(cookbooks_display.get(cookbooks_display.curselection())), **self.BUTTON_STYLE)
        show_info_button.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.shop_menu, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
        
    def display_cookbook(self, cookbook_name: str):
        self.clear_screen()
        displayed_cookbook: Cookbook = Cookbook(cookbook_name, self.connection)
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        cookbook_info_display = tk.Label(menu_frame, text=f"{displayed_cookbook.name}:\nFor Area: {displayed_cookbook.area}\nPrice: {displayed_cookbook.price}", **self.PANEL_STYLE)
        cookbook_info_display.pack(**self.LABEL_PACK)
        show_money_label = tk.Label(menu_frame, text=f"You have {self.restaurant_obj.money} money left!", **self.LABEL_STYLE)
        show_money_label.pack(**self.LABEL_PACK)
        purchase_button = tk.Button(menu_frame, text="Purchase", command=lambda: self.cookbook_purchase_wrapper(displayed_cookbook), **self.BUTTON_STYLE)
        purchase_button.pack(**self.BUTTON_PACK)
        back_button = tk.Button(menu_frame, text="Back", command=self.cookbooks_shop, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
        
    def cookbook_purchase_wrapper(self, cookbook_obj: Cookbook):
        self.clear_screen()
        if self.restaurant_obj.money >= cookbook_obj.price:
            self.restaurant_obj.money -= cookbook_obj.price
            self.restaurant_obj.update_money()
            # Adds cookbook to restaurant
            self.restaurant_obj.unlock_cookbook(cookbook_obj.name)
            menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
            menu_frame.pack(expand=True)
            cookbook_purchase_confirmation = tk.Label(menu_frame, text=f"You bought {cookbook_obj.name} for {cookbook_obj.price}!\nYou have {self.restaurant_obj.money} money remaining", **self.LABEL_STYLE)
            cookbook_purchase_confirmation.pack(**self.LABEL_PACK)
            ok_button = tk.Button(menu_frame, text="Yay!", command=self.shop_menu, **self.BUTTON_STYLE)
            ok_button.pack(**self.BUTTON_PACK)
        else: 
            self.youre_broke()
        
    # Displays when the user doesn't have enough money to buy something
    def youre_broke(self):
        self.clear_screen()
        messagebox.showerror(message="You don't have enough money to purchase that")
        self.shop_menu()
        
    # Menu for ending the game
    def end_game(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        you_sure_label = tk.Label(menu_frame, text="Are you sure you want to end your run here?", **self.LABEL_STYLE)
        you_sure_label.pack(**self.LABEL_PACK)
        yes_button = tk.Button(menu_frame, text="Yes", command=self.end_game_logic, **self.BUTTON_STYLE)
        yes_button.pack(**self.BUTTON_PACK)
        no_button = tk.Button(menu_frame, text="No", command= self.next_day, **self.BUTTON_STYLE)
        no_button.pack(**self.BUTTON_PACK)
        
    # Runs the logic for ending the game
    def end_game_logic(self):
        self.clear_screen()
        end_game_call(self.connection, self.room_ID)
        messagebox.showinfo(message="Thanks for playing!")
        self.quit_game()
    
    # Menu for starting the day and associated logic
    def next_day(self):
        self.clear_screen()
        rent: int = self.RENT_SCALAR * self.num_players * self.restaurant_obj.day
        self.restaurant_obj.update_restaurant()
        #Set default value
        didnt_die = True
        if self.is_host == True:
            # Host setup stuff
            didnt_die = self.next_day_setup_host()
        else:
            self.next_day_non_host()
        if didnt_die == True:
            self.next_day_screen(rent)
        # If you lose during post day calcs:
        else:
            menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
            menu_frame.pack(expand=True)
            lost_label = tk.Label(menu_frame, text="You couldn't pay rent, or ran out of reputation this day. Your restaurant has been shut down and purchased by your mean uncle, Gustave.\n You're now unemployed. Go get a job", **self.LABEL_STYLE)
            lost_label.pack(**self.LABEL_PACK)
            accept_defeat_button = tk.Button(menu_frame, text="Time to go back to working fast food...", command=self.quit_game, **self.BUTTON_STYLE)
            accept_defeat_button.pack(**self.BUTTON_PACK)
            
    def next_day_non_host(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        if check_day(self.connection, self.room_ID) == -1:
            lost_label = tk.Label(menu_frame, text="You couldn't pay rent, or ran out of reputation this day. Your restaurant has been shut down and purchased by your mean uncle, Gustave.\n You're now unemployed. Go get a job", **self.LABEL_STYLE)
            lost_label.pack(**self.LABEL_PACK)
            accept_defeat_button = tk.Button(menu_frame, text="Time to go back to working fast food...", command=self.quit_game, **self.BUTTON_STYLE)
            accept_defeat_button.pack(**self.BUTTON_PACK)
        else:
            waiting_label = tk.Label(menu_frame, text="The day is over. Please wait for the host to start the next day", **self.LABEL_STYLE)
            waiting_label.pack(**self.LABEL_PACK)
            next_day_button = tk.Button(menu_frame, text="Next Day", command=self.host_ready_for_next_day, **self.BUTTON_STYLE)
            next_day_button.pack(**self.BUTTON_PACK)
            
            
    def next_day_screen(self, rent):
        self.clear_screen()
        self.restaurant_obj.update_restaurant()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        title_label = tk.Label(menu_frame, text=f"You're about to begin day {self.restaurant_obj.day}!", **self.TITLE_STYLE)
        title_label.pack(**self.TITLE_PACK)
        rent_label = tk.Label(menu_frame, text=f"You paid {rent} in rent\nYou have {self.restaurant_obj.money} money left and {self.restaurant_obj.reputation} reputation", **self.LABEL_STYLE)
        rent_label.pack(**self.LABEL_PACK)
        start_button = tk.Button(menu_frame, text="Start day!", command=self.host_ready_for_next_day, **self.BUTTON_STYLE)
        start_button.pack(**self.BUTTON_PACK)
        if self.is_host == True:
            end_game_button = tk.Button(menu_frame, text="End the game", command=self.end_game, **self.BUTTON_STYLE)
            end_game_button.pack(**self.BUTTON_PACK)
        
    # Host-only logic for setting up the next day        
    def next_day_setup_host(self) -> bool:
        # Conditions for checking if you've lost the game
        # Pay rent
        self.restaurant_obj.money -= self.RENT_SCALAR * self.num_players * self.restaurant_obj.day
        self.restaurant_obj.update_money()
        # Update reputation
        if len(self.restaurant_obj.customers) > 0:
            self.restaurant_obj.reputation -= (len(self.restaurant_obj.customers) * self.num_players * self.restaurant_obj.day)
        self.restaurant_obj.reputation += 5
        # Do not exceed 200 reputation
        if self.restaurant_obj.reputation > 200:
            self.restaurant_obj.reputation = 200
        self.restaurant_obj.update_reputation()
        self.restaurant_obj.update_restaurant()
        
        # The restaurant lives on
        if self.restaurant_obj.money > 0 and self.restaurant_obj.reputation > 0:
            increment_day(self.connection, self.room_ID)
            self.num_players = len(get_all_players(self.connection, self.room_ID))
            self.restaurant_obj.update_restaurant()
            self.restaurant_obj.create_customers(self.num_players)
            set_time(self.connection, int(time.time()) + self.TIME_CONSTRAINT_SECONDS, self.room_ID)
            return True
        else:
            return False
        
    # Checks to see if the host has started the next dau
    def host_ready_for_next_day(self) -> None:
        if self.restaurant_obj.day == check_day(self.connection, self.room_ID) and self.is_host == False:
            messagebox.showwarning(message="The host hasn't begun the next day. Please wait")
            self.next_day()
        else:
            self.restaurant_obj.update_restaurant()
            messagebox.showinfo(message=f"You begin day {self.restaurant_obj.day}\nGood luck!")
            self.restaurant_menu()
            
    # Main menu for the database editor feature
    def database_editor_main_menu(self):
        self.clear_screen()
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        # This title is a Button in the original code, so it is styled flat to look like a heading
        editor_title_label = tk.Button(menu_frame, text="Database Editor\nSelect which category of entry you would like to add to the database", relief="flat", bd=0, activebackground=self.BACKGROUNDCOLOR, activeforeground=self.TEXT_COLOR, **self.TITLE_STYLE)
        editor_title_label.pack(**self.TITLE_PACK)
        # Add ingredients
        add_ingredient_button = tk.Button(menu_frame, text="Add Ingredient", command=self.add_ingredient_menu, **self.BUTTON_STYLE)
        add_ingredient_button.pack(**self.BUTTON_PACK)
        # Add recipes
        add_recipe_button = tk.Button(menu_frame, text="Add Recipe", **self.BUTTON_STYLE)
        add_recipe_button.pack(**self.BUTTON_PACK)
        # Add cookbooks
        add_cookbook_button = tk.Button(menu_frame, text="Add Cookbook", **self.BUTTON_STYLE)
        add_cookbook_button.pack(**self.BUTTON_PACK)
        # Add enemies
        add_enemy_button = tk.Button(menu_frame, text="Add Enemy", **self.BUTTON_STYLE)
        add_enemy_button.pack(**self.BUTTON_PACK)
        # Add areas
        add_area_button = tk.Button(menu_frame, text="Add Area", **self.BUTTON_STYLE)
        add_area_button.pack(**self.BUTTON_PACK)
        # Quit
        back_button = tk.Button(menu_frame, text="Back", command=self.main_menu, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
        
    # Menu for adding an ingredient
    def add_ingredient_menu(self):
        self.clear_screen()
        areas_list: list[str] = get_area_names(self.connection, self.room_ID)
        menu_frame = tk.Frame(self.root, **self.FRAME_STYLE)
        menu_frame.pack(expand=True)
        # This title is a Button in the original code, so it is styled flat to look like a heading
        editor_title_label = tk.Button(menu_frame, text="Add an ingredient", relief="flat", bd=0, activebackground=self.BACKGROUNDCOLOR, activeforeground=self.TEXT_COLOR, **self.TITLE_STYLE)
        editor_title_label.pack(**self.TITLE_PACK)
        enter_name = tk.Label(menu_frame, text="Ingredient name:", **self.LABEL_STYLE)
        enter_name.pack(**self.LABEL_PACK)
        enter_name_entry = tk.Entry(menu_frame, **self.ENTRY_STYLE)
        enter_name_entry.pack(**self.LABEL_PACK)
        select_type_label = tk.Label(menu_frame, text="Select ingredient type", **self.LABEL_STYLE)
        select_type_label.pack(**self.LABEL_PACK)
        select_type_entry = tk.Listbox(menu_frame, width=self.LISTBOX_WIDTH, height=self.LISTBOX_SHORT_HEIGHT, **self.LISTBOX_STYLE)
        select_type_entry.pack(**self.LABEL_PACK)
        select_type_entry.insert(0, *["fish", "plant", "meat"])
        select_area_label = tk.Label(menu_frame, text="What area(s) should this ingredient be found in?", **self.LABEL_STYLE)
        select_area_label.pack(**self.LABEL_PACK)
        # Frame holds the listbox and its scrollbar
        select_area_list_frame = tk.Frame(menu_frame, **self.FRAME_STYLE)
        select_area_list_frame.pack(**self.LABEL_PACK)
        select_area_scrollbar = tk.Scrollbar(select_area_list_frame)
        select_area_scrollbar.pack(side="right", fill="y")
        select_area_dropdown = tk.Listbox(select_area_list_frame, selectmode="multiple", yscrollcommand=select_area_scrollbar.set, width=self.LISTBOX_WIDTH, height=self.LISTBOX_SHORT_HEIGHT, **self.LISTBOX_STYLE)
        select_area_dropdown.insert(0, *areas_list)
        select_area_dropdown.pack(side="left", fill="both", expand=True)
        select_area_scrollbar.config(command=select_area_dropdown.yview)
        
        # add_ingredient_submit = tk.Button(self.root, text="Go!", command=lambda: self.add_ingredient_weight(enter_name_entry.get(), select_type_entry.curselection(), select_area_dropdown.curselection(), areas_list, 0))
        # add_ingredient_submit.pack()
        
        
        back_button = tk.Button(menu_frame, text="Back", command=self.database_editor_main_menu, **self.BUTTON_STYLE)
        back_button.pack(**self.BUTTON_PACK)
    
    # # Add weights for ingredients in different areas
    # def add_ingredient_weight(self, ingredient_name: str, ingredient_type: str, selected_area_indexes: list[int], areas_list: list[str], i: int):
    #     self.clear_screen()
    #     weight_label = tk.Label(self.root, text=f"What weight would you like this ingredient to have in {areas_list[selected_area_indexes[i]]}?")
    #     weight_label.pack()
    #     weight_entry = tk.Entry(self.root)
    #     weight_entry.pack()
    #     submit_button = tk.Button(self.root, text="Submit", command=lambda: submit_editor_ingredient(self.connection, ingredient_name=ingredient_name, ingredient_type=ingredient_type, area_name=areas_list[selected_area_indexes[i]], ingredient_weight=int(weight_entry.get())))
    #     submit_button.pack()
