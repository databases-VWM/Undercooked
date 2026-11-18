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

#MySQL default connection


# user_ID = generate_user_ID(connection)

#Holds the game logic
class GameInstance:
    def __init__(self, root):
        self.root = root
        self.BACKGROUNDCOLOR = "lightgray"
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
        # list of tuples of (ingredient, quantity)
        self.local_inventory: list[tuple[str, int]] = []
        self.current_area: Area
        self.checkpoints: dict[str, int] = {}
        self.combat_log: list[str] = []
        self.connection = None
        self.restaurant_obj: Restaurant
        self.weapon: Weapon = Weapon("Frying Pan")
        self.armor: Armor = Armor("Chef's Garbs")

    # Clears the screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            del widget
        self.root.configure(bg=self.BACKGROUNDCOLOR)

    #This lets the player, at game start, choose which database they are connecting to
    def database_select_screen(self):
        self.clear_screen()
        database_label = tk.Label(self.root, text="Please select which database you are playing on. If you are hosting, leave all these values as their defaults")
        database_label.pack()
        ip_addr_label = tk.Label(self.root, text="IP Address:")
        ip_addr_label.pack()
        ip_addr_entry = tk.Entry(self.root)
        #Sets default text
        ip_addr_entry.insert(0, "localhost")
        ip_addr_entry.pack()
        # port_label = tk.Label(self.root, text="Port:")
        # port_label.pack()
        # port_entry = tk.Entry(self.root)
        # port_entry.insert(0, "3306")
        # port_entry.pack()
        continue_button = tk.Button(self.root, text="Continue", command= lambda: [self.setup_database_connection(ip_addr_entry.get()), self.login()])
        continue_button.pack()
        
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
        login_label = tk.Label(self.root, text="Please input your User ID and password to login!\nOr, create a new user below")
        login_label.pack()
        userID_entry = tk.Entry(self.root)
        userID_entry.pack()
        password_entry = tk.Entry(self.root)
        password_entry.pack()
        #Checks for the UserID. If it exists, go to main menu. Else, reopen login
        login_button = tk.Button(self.root, text="Login", command=lambda: self.login_logic(userID_entry.get(), password_entry.get()))
        login_button.pack()
        register_user_button = tk.Button(self.root, text="Register a New User", command=self.register)
        register_user_button.pack()

    # Handles the logic of the input button
    # DONE Wesley(1): Write function to the database that returns true if the user is logged into a room and false if not
    # is_duplicate_connection(connection, userID: str) -> bool
    def login_logic(self, userID: str, password: str):
        # Check for if username and password are correct
        # Wesley(3): Check menu_functions.py for info
        correct_login = check_login_info(self.connection, userID, password)
        if correct_login == True:
            # Checks to see if the user already has a connection
            if is_logged_in(self.connection, userID) == False:
                self.userID = userID
                #Creates player
                self.player = Entity("Player", True)
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
    #Wesley(2): Write function that sets the in_use database attribute to either true or false and sets room_ID to NULL
    # def set_log_in(connection, what_to_set_it_to: bool, user_id) -> None
    def duplicate_connection(self, userID, password):
        self.clear_screen()
        duplicate_connection_label = tk.Label(self.root, text="You are already logged in somewhere else. Would you like to make a new connection?")
        duplicate_connection_label.pack()
        yes_connect_button = tk.Button(self.root, text="Yes", command= lambda: [set_log_in(self.connection, False, userID), self.login_logic(userID, password)])
        yes_connect_button.pack()
        no_connect_button = tk.Button(self.root, text="No", command=self.login)
        no_connect_button.pack()

    # Handles creation of new user
    def register(self):
        self.clear_screen()
        title = tk.Label(self.root, text="Create your user!\nInput your username")
        title.pack()
        username_input = tk.Entry(self.root)
        username_input.pack()
        password_entry = tk.Entry(self.root)
        password_entry.pack()
        register_button = tk.Button(self.root, text="Register User!", command=lambda: self.register_user(username_input.get(), password_entry.get()))
        register_button.pack()

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
        user_id_label = tk.Label(self.root, text=f"This is your user ID! \nWrite this down so you can log back in!\n{self.userID}")
        user_id_label.pack()
        ok_button = tk.Button(self.root, text="Ok!", command=self.main_menu)
        ok_button.pack()

    # Overall main menu
    def main_menu(self):
        # Reset is_host
        self.is_host = False
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
        ip_addr = get_local_ip()
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
        # room_IP_button = tk.Entry(self.root)
        # room_IP_button.pack()
        room_ID_button = tk.Entry(self.root)
        room_ID_button.pack()
        join_room_button = tk.Button(self.root, text="Join Room", command=lambda: self.join_room(room_ID_button.get()))
        join_room_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.main_menu)
        back_button.pack()

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

        room_name_label = tk.Label(self.root, text=self.room_name)
        room_name_label.pack()
        room_ID_label = tk.Label(self.root, text="Room ID: " + str(self.room_ID))
        room_ID_label.pack()
        IP_address_button = tk.Button(self.root, text="Show IP Address", command=self.show_IP)
        IP_address_button.pack()
        players_list = tk.Label(self.root, textvariable=current_players_list)
        players_list.pack()
        update_players_list_button = tk.Button(self.root, text="Refresh Player List", command=self.waiting_room_host)
        update_players_list_button.pack()
        start_button = tk.Button(self.root, text="Start Game", command=self.start_day)
        start_button.pack()
    
    # Starts the game (database setup from the host)
    def start_day(self):
        increment_day(self.connection, self.room_ID)
        self.has_game_started()

    # This is where the guests wait
    # Wesley (6): Write a function called check_day that returns the current day for the given room
    def waiting_room_guest(self):
        self.clear_screen()
        
        # Sets logged in status
        set_log_in(self.connection, True, self.userID)
        
        # Retrieves names of all players
        current_players_list = tk.StringVar()
        current_players_list.set(setup_for_stringvar(get_all_players(self.connection, self.room_ID)))
        
        room_name_label = tk.Label(self.root, text=self.room_name)
        room_name_label.pack()
        room_ID_label = tk.Label(self.root, text="ID: " + str(self.room_ID))
        room_ID_label.pack()
        IP_address_button = tk.Button(self.root, text="Show IP Address", command=self.show_IP)
        IP_address_button.pack()
        waiting_button = tk.Label(self.root, text="Waiting for host to start game")
        waiting_button.pack()
        players_list = tk.Label(self.root, textvariable=current_players_list)
        players_list.pack()
        update_players_list_button = tk.Button(self.root, text="Refresh Player List", command=self.waiting_room_guest)
        update_players_list_button.pack()
        join_game_button = tk.Button(self.root, text="Join Game", command=self.has_game_started)
        join_game_button.pack()
        #Show all other players in the room, room ID, and room name
    
    #Function for determining if players can actually join the game
    def has_game_started(self):
        day_num: int = check_day(self.connection, self.room_ID)
        if day_num > 0:
            increment_day(self.connection, self.room_ID)
            messagebox.showinfo(message="You have successfully joined the game!")
            # Creates restaurant object
            self.restaurant_obj = Restaurant(self.room_name, self.room_ID, self.connection)
            self.restaurant_menu()
        else:
            messagebox.showerror(message="The game hasn't started yet. You will be able to join when the host starts the game")
            self.waiting_room_guest()
            

    # This is the menu that first opens when the game starts
    def restaurant_menu(self):
        self.restaurant_obj.update_restaurant()
        self.clear_screen()
        self.player = Entity(get_username(self.connection, self.userID), True)
        self.player.health = self.player.max_health
        cook_button = tk.Button(self.root, text="Cook", command=self.cook_menu)
        cook_button.pack()
        equipment_button = tk.Button(self.root, text="Equipment", command=self.equipment_menu)
        equipment_button.pack()
        shop_button = tk.Button(self.root, text="Shop", command=self.shop_menu)
        shop_button.pack()
        status_button = tk.Button(self.root, text="Check Restaurant Status", command=self.restaurant_status)
        status_button.pack()
        rpg_switch_button = tk.Button(self.root, text="To the Wilderness", command=self.wilderness_area_select)
        rpg_switch_button.pack()

    # This is the menu that opens to let the player choose which area they are going to
    def wilderness_area_select(self):
        selected_area = tk.StringVar(self.root)
        selected_area.set("Select an Area")
        unlocked_areas_list = get_item_names("areas")
        select_checkbox = tk.BooleanVar(self.root)
        self.clear_screen()
        
        ingredients_forecast = tk.StringVar()
        ingredients_forecast.set(setup_ingredients_forecast(selected_area.get()))
        # Sets up frame for the ingredient forecast
        ingredients_forecast_frame = tk.Frame(self.root)
        ingredients_forecast_frame.pack(side="right")
        ingredients_forecast_box = tk.Label(ingredients_forecast_frame, textvariable=ingredients_forecast)
        ingredients_forecast_box.pack(fill="both")
        

        wilderness_title = tk.Label(self.root, text="Welcome to the Wilderness!\nSelect an Area!")
        wilderness_title.pack()
        areas_dropdown = tk.OptionMenu(self.root, selected_area, *unlocked_areas_list) 
        """TODO at some point: command=ingredients_forecast.set(setup_ingredients_forecast(selected_area.get()))"""
        areas_dropdown.pack()
        show_forecast_button = tk.Button(self.root, text="Show area ingredient forecast", command= lambda: ingredients_forecast.set(setup_ingredients_forecast(selected_area.get())))
        show_forecast_button.pack()
        checkpoint_checkbox = tk.Checkbutton(self.root, text="Start From Checkpoint?", variable=select_checkbox, onvalue=True, offvalue=False)
        checkpoint_checkbox.pack()
        go_to_wilderness = tk.Button(self.root, text="Go!", command= lambda: self.check_area_select(selected_area.get(), select_checkbox.get()))
        go_to_wilderness.pack()
        
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
            self.current_area = Area(selected_area_name)
            # Sets checkpoint if there is one
            if self.current_area.current_node != checkpoint_num:
                self.current_area.current_node = checkpoint_num
            # Calls the iterative node function
            self.explore_node()

    # This function overall handles nodes. It acts like a loop
    # This function specifically has the menu for campsites and checkpoints
    # This series of functions is kind of like Assembly labels due to how TKinter works. 
    def explore_node(self, pause_zone = False):
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
            campsite_label = tk.Label(self.root, text="Welcome to the campsite\nPick one of the following")
            campsite_label.pack()
            check_status_button = tk.Button(self.root, text="Check Status", command=self.check_player_status)
            check_status_button.pack()
            full_heal_button = tk.Button(self.root, text="Full Heal", command=self.full_heal_menu)
            full_heal_button.pack()
            return_inventory_button = tk.Button(self.root, text="Return ingredients to restaurant and heal 25% of your health", command=self.half_and_half)
            return_inventory_button.pack()
            return_to_restaurant_button = tk.Button(self.root, text="Return to the restaurant", command=self.restaurant_menu)
            return_to_restaurant_button.pack()
            #Checkpoint additional logic
            if self.current_area.current_node % 10 == 0:
                set_checkpoint_button = tk.Button(self.root, text="Set a checkpoint", command=self.set_checkpoint)
                set_checkpoint_button.pack()
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
        ingredients_inventory.set(print_ingredients(self.local_inventory)) # type: ignore
        
        player_status_label = tk.Label(self.root, textvariable=player_status)
        player_status_label.pack()
        ingredients_inventory_display = tk.Label(self.root, textvariable=ingredients_inventory)
        ingredients_inventory_display.pack()
        current_zone = tk.Label(self.root, text=f"Current Node: {self.current_area.current_node}")
        current_zone.pack()
        current_area_checkpoint = tk.Label(self.root, text=f"Current Checkpoint: Node {self.get_checkpoint()}")
        current_area_checkpoint.pack()
        ok_button = tk.Button(self.root, text="Continue", command=lambda: self.explore_node(True))
        ok_button.pack()
    
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
        text_label = tk.Label(self.root, text="You heal to full health")
        text_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.explore_node)
        ok_button.pack()

    # Heal 25% health and return inventory to restaurant
    def half_and_half(self):
        self.clear_screen()
        # Sends off your inventory to the database
        # Uncomment when Ingredients JSON is ready
        #inv_to_database(connection, self.room_ID, self.local_inventory)
        self.local_inventory = []
        self.player.health += round(self.player.max_health * .25)
        # Don't allow for going over max health
        if self.player.health > self.player.max_health:
            self.player.health = self.player.max_health
        text_label = tk.Label(self.root, text="You heal 25% of your health and send your inventory back to the restaurant")
        text_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.explore_node)
        ok_button.pack()

    # Node type text
    def node_type_text(self):
        self.clear_screen()
        # Sets flavor message for popup to signify node type
        # TODO: Maybe do random messages of each type to add a little more flavor
        if self.current_area.node_type == "fishing":
            node_type_message = "This looks like a great spot to go FISHING!"
        elif self.current_area.node_type == "flora":
            node_type_message = "It looks like you could harvest some delicious PLANTS around here"
        elif self.current_area.node_type == "fauna":
            node_type_message = "One might say this would be a great spot to go HUNTING"
        
        gather_label = tk.Label(self.root, text=node_type_message)
        gather_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.is_there_an_enemy)
        ok_button.pack()

    def is_there_an_enemy(self):
        if self.current_area.is_enemy == True:
            self.enemy_node_text()
        else:
            self.harvest_node_text()

    def enemy_node_text(self):
        self.clear_screen()
        self.current_enemy = Entity(self.current_area.enemy_name)
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
        
        text_label = tk.Label(self.root, text=enemy_message)
        text_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.battle_menu)
        ok_button.pack()

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

            
        text_label = tk.Label(self.root, text=f"You harvested: \n{setup_for_stringvar(node_ingredients)}")
        text_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.explore_node)
        ok_button.pack()

    # Text for if the character falls
    def fallen_text(self):
        self.clear_screen()
        # Removes the checkpoint in the area
        if self.get_checkpoint() != 0:
            self.remove_checkpoint()
        gather_label = tk.Label(self.root, text="You run back to the restaurant injured, dropping all of your ingredients along the way")
        gather_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.restaurant_menu)
        ok_button.pack()

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
        stats_frame = tk.Frame(self.root)
        stats_frame.pack(side="left", fill="both")
        combat_log_frame = tk.Frame(self.root)
        combat_log_frame.pack(side="right", fill="both")
        combat_buttons_frame = tk.Frame(self.root)
        combat_buttons_frame.pack()
        # combat_buttons_frame.pack(side="bottom")
        
        # Displays
        player_stats_screen = tk.Label(stats_frame, textvariable=local_player_stats)
        player_stats_screen.pack(fill="both")
        enemy_stats_screen = tk.Label(stats_frame, textvariable=local_enemy_stats)
        enemy_stats_screen.pack(fill="both")
        combat_log_menu = tk.Label(combat_buttons_frame, textvariable=local_combat_log)
        combat_log_menu.pack(fill="both")
        
        # Button Menu
        attack_button = tk.Button(combat_buttons_frame, text="Attack", command=self.wrapper_attack)
        attack_button.pack(fill="both", side="left")
        
        parry_button = tk.Button(combat_buttons_frame, text="Parry", command=self.wrapper_parry)
        parry_button.pack(fill="both", side="left")
        
        guard_button = tk.Button(combat_buttons_frame, text="Guard", command=self.wrapper_guard)
        guard_button.pack(fill="both", side="left")
        
        flee_button = tk.Button(combat_buttons_frame, text="Flee(Cowardly)", command=self.wrapper_flee)
        flee_button.pack(fill="both", side="left")
    
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
            enemy_slain_label = tk.Label(self.root, text=enemy_defeated_text)
            enemy_slain_label.pack()
            enemy_slain_ok = tk.Button(self.root, text="Ok!", command=self.harvest_node_text)
            enemy_slain_ok.pack()
        else: 
            self.battle_menu()
    
    def is_player_alive(self):
        if self.player.health > 0:
            self.is_enemy_slain()
        else:
            self.fallen_text()
        
    def get_checkpoint(self) -> int:
        checkpoint_num = 0
        try:
            checkpoint_num = self.checkpoints[self.current_area.name]
        except KeyError:
            checkpoint_num = 0
        return checkpoint_num
    
    def cook_menu(self):
        pass
    
    # Allows for equipping weapons and armor
    def equipment_menu(self):
        self.clear_screen()
        equipment_label = tk.Label(self.root, text="Equip yourself!")
        equipment_label.pack()
        weapon_equip = tk.Button(self.root, text="Weapons", command=self.weapon_select_menu)
        weapon_equip.pack()
        armor_equip = tk.Button(self.root, text="Armor", command=self.armor_select_menu)
        armor_equip.pack()
        back_button = tk.Button(self.root, text="Back", command=self.restaurant_menu)
        back_button.pack()
        
    # Menu for equipping a weapon
    def weapon_select_menu(self):
        inspected_weapon: Weapon
        weapon_stats = tk.StringVar()
        weapon_stats.set("No weapon selected to inspect")
        
        self.clear_screen()
        # Setting up frames
        left_frame = tk.Frame(self.root)
        left_frame.pack(side="left", fill="both")
        middle_frame = tk.Frame(self.root)
        middle_frame.pack(side="left", fill="both")
        right_frame = tk.Frame(self.root)
        right_frame.pack(side="left", fill="both")
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x")
        
        # Setting up menus
        weapons_inventory_label = tk.Label(left_frame, text="Weapons Inventory")
        weapons_inventory_label.pack()
        weapons_inventory = tk.Listbox(left_frame, selectmode="single")
        #NOTE: Wesley, write a query that pulls all weapons from the inventory. Maybe write a generic function that pulls all names for a type_id and room_id instead?
        inventory_weapons_list: list[str] = [] #Insert function here. Make sure it returns an array of strings
        weapons_inventory.insert(0, *inventory_weapons_list)
        
        selected_weapon_compare = tk.Label(middle_frame, textvariable=weapon_stats)
        selected_weapon_compare.pack(fill="both")
        
        # Sets what weapon's stats to show in the inspector menu
        inspect_weapon_button = tk.Button(bottom_frame, text="Inspect Selected Weapon", command=lambda: weapon_stats.set(""))
        inspect_weapon_button.pack()
        
        back_button = tk.Button(bottom_frame, text="Back", command=self.restaurant_menu)
        back_button.pack()
        
    
    # Menu for equipping armor
    def armor_select_menu(self):
        pass
    
    # Displays the status of the restaurant
    def restaurant_status(self):
        self.clear_screen()
        restaurant_name_label = tk.Label(self.root, text=f"{self.restaurant_obj.restaurant_name}")
        restaurant_name_label.pack()
        restaurant_money_label = tk.Label(self.root, text=f"Money: {self.restaurant_obj.money}")
        restaurant_money_label.pack()
        day_label = tk.Label(self.root, text=f"Day: {self.restaurant_obj.day}")
        day_label.pack()
        ingredient_inventory_label = tk.Label(self.root, text=f"Ingredients Inventory: {print_ingredients(self.restaurant_obj.inventory)}")
        ingredient_inventory_label.pack()
        player_status_label = tk.Label(self.root, text="Your character's stats:\n")
        player_status_label.pack()
        player_status = tk.StringVar()
        player_status.set(setup_for_stringvar(output_entity_stats(self.player, True)))
        weapon_info_display = tk.Label(self.root, text=f"Equipment:\n\n{self.weapon.name}:\nAttack Roll: {transform_dice_to_str(self.weapon.attack_dice)}\n Average Damage: {dice_avg(self.weapon.attack_dice)}\nAttack Modifier: {self.weapon.modifier}\nPrice: {self.weapon.price}")
        weapon_info_display.pack()
        armor_info_display = tk.Label(self.root, text=f"{self.armor.name}:\n Type: {self.armor.type}\nDefense: {self.armor.defense}\n Block Dice: {transform_dice_to_str(self.armor.block_dice)}\nDodge Dice: {transform_dice_to_str(self.armor.dodge_dice)}\nPrice: {self.armor.price}")
        armor_info_display.pack()
        continue_button = tk.Button(self.root, text="Back to work!", command=self.restaurant_menu)
        continue_button.pack()

    #Overarching menu for the shop
    def shop_menu(self):
        self.clear_screen()
        weapons_shop_button = tk.Button(self.root, text="Weapons", command=self.weapons_shop)
        weapons_shop_button.pack()
        armors_shop_button = tk.Button(self.root, text="Armor", command=self.armors_shop)
        armors_shop_button.pack()
        cookbooks_shop_button = tk.Button(self.root, text="Cookbooks", command=self.cookbooks_shop)
        cookbooks_shop_button.pack()
        quit_shop_button = tk.Button(self.root, text="Back", command=self.restaurant_menu)
        quit_shop_button.pack()
        
    # Displays all weapons available for sale
    def weapons_shop(self):
        self.clear_screen()
        weapons_display = tk.Listbox(self.root, selectmode="single")
        weapons_display.pack()
        weapons_array: list[str] = get_item_names("weapons")
        weapons_display.insert(0, *weapons_array)
        
        show_info_button = tk.Button(self.root, text="Inspect", command=lambda: self.display_weapon(weapons_display.get(weapons_display.curselection())))
        show_info_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.shop_menu)
        back_button.pack()
            
    # Shows information about the currently selected weapon
    def display_weapon(self, current_weapon: str):
        self.clear_screen()
        displayed_weapon: Weapon = Weapon(current_weapon)
        weapon_info_display = tk.Label(self.root, text=f"{displayed_weapon.name}:\nAttack Roll: {transform_dice_to_str(displayed_weapon.attack_dice)}\n Average Damage: {dice_avg(displayed_weapon.attack_dice)}\nAttack Modifier: {displayed_weapon.modifier}\nPrice: {displayed_weapon.price}")
        weapon_info_display.pack()
        show_money_label = tk.Label(self.root, text=f"You have {self.restaurant_obj.money} money left!")
        show_money_label.pack()
        purchase_button = tk.Button(self.root, text="Purchase", command=lambda: self.weapon_purchase_wrapper(displayed_weapon))
        purchase_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.weapons_shop)
        back_button.pack()
        
    # Database logic for purchasing the weapon
    def weapon_purchase_wrapper(self, new_weapon: Weapon):
        # Check for money
        self.clear_screen()
        if self.restaurant_obj.money >= new_weapon.price:
            self.restaurant_obj.money -= new_weapon.price
            #NOTE: Wesley, write a function that takes in the connection, weapon object, and room_id and pushes to shop queue table
            # Make it generic so it can be used for armor and weapons
            weapon_purchase_confirmation = tk.Label(self.root, text=f"You bought {new_weapon.name} for {new_weapon.price}!\nYou have {self.restaurant_obj.money} money remaining")
            weapon_purchase_confirmation.pack()
            ok_button = tk.Button(self.root, text="Yay!", command=self.shop_menu)
            ok_button.pack()
        else:
            self.youre_broke()
        
    # Same as above but for armor
    def armors_shop(self):
        self.clear_screen()
        armors_display = tk.Listbox(self.root, selectmode="single")
        armors_display.pack()
        armors_array: list[str] = get_item_names("armors")
        armors_array.insert(0, *armors_array)
    
        show_info_button = tk.Button(self.root, text="Inspect", command=lambda: self.display_armor(armors_display.get(armors_display.curselection())))
        show_info_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.shop_menu)
        back_button.pack()
    
    def display_armor(self, current_armor: str):
        self.clear_screen()
        displayed_armor: Armor = Armor(current_armor)
        armor_info_display = tk.Label(self.root, text=f"{displayed_armor.name}:\n Type: {displayed_armor.type}\nDefense: {displayed_armor.defense}\n Block Dice: {transform_dice_to_str(displayed_armor.block_dice)}\nDodge Dice: {transform_dice_to_str(displayed_armor.dodge_dice)}\nPrice: {displayed_armor.price}")
        armor_info_display.pack()
        show_money_label = tk.Label(self.root, text=f"You have {self.restaurant_obj.money} money left!")
        show_money_label.pack()
        purchase_button = tk.Button(self.root, text="Purchase", command=lambda: self.armor_purchase_wrapper(displayed_armor))
        purchase_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.armors_shop)
        back_button.pack()
        
    def armor_purchase_wrapper(self, new_armor: Armor):
        self.clear_screen()
        if self.restaurant_obj.money >= new_armor.price:
            self.restaurant_obj.money -= new_armor.price
            #NOTE: Wesley, put the same function here
            armor_purchase_confirmation = tk.Label(self.root, text=f"You bought {new_armor.name} for {new_armor.price}!\nYou have {self.restaurant_obj.money} money remaining")
            armor_purchase_confirmation.pack()
            ok_button = tk.Button(self.root, text="Yay!", command=self.shop_menu)
            ok_button.pack()
        else:
            self.youre_broke()
    
    # This one is a bit different
    def cookbooks_shop(self):
        self.clear_screen()
        cookbooks_display = tk.Listbox(self.root, selectmode="single")
        cookbooks_display.pack()
        local_cookbooks_array: list[str] = get_item_names("cookbooks")
        #Removes already purchased cookbooks from display
        for purchased_cookbook in self.restaurant_obj.onetime_purchases:
            local_cookbooks_array.remove(purchased_cookbook)
            
        cookbooks_display.insert(0, *local_cookbooks_array)
        
        show_info_button = tk.Button(self.root, text="Inspect", command=lambda: self.display_cookbook(cookbooks_display.get(cookbooks_display.curselection())))
        show_info_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.shop_menu)
        back_button.pack()
        
    def display_cookbook(self, cookbook_name: str):
        self.clear_screen()
        displayed_cookbook: Cookbook = Cookbook(cookbook_name)
        cookbook_info_display = tk.Label(self.root, text=f"{displayed_cookbook.name}:\nFor Area: {displayed_cookbook.area}\nPrice: {displayed_cookbook.price}")
        cookbook_info_display.pack()
        show_money_label = tk.Label(self.root, text=f"You have {self.restaurant_obj.money} money left!")
        show_money_label.pack()
        purchase_button = tk.Button(self.root, text="Purchase", command=lambda: self.cookbook_purchase_wrapper(displayed_cookbook))
        purchase_button.pack()
        back_button = tk.Button(self.root, text="Back", command=self.cookbooks_shop)
        back_button.pack()
        
    def cookbook_purchase_wrapper(self, cookbook_obj: Cookbook):
        self.clear_screen()
        if self.restaurant_obj.money >= cookbook_obj.price:
            self.restaurant_obj.money -= cookbook_obj.price
            # Adds cookbook to restaurant
            self.restaurant_obj.onetime_purchases.append(cookbook_obj.name)
            #NOTE: Wesley, write a function to push the new cookbook purchase up to the database (shop queue table) AND then one of Max's advanced SQL bits should update the cookbooks table
            # I just updated the Cookbooks table to remove the bool for if purchased. If an entry is in the table, it's purchased
            cookbook_purchase_confirmation = tk.Label(self.root, text=f"You bought {cookbook_obj.name} for {cookbook_obj.price}!\nYou have {self.restaurant_obj.money} money remaining")
            cookbook_purchase_confirmation.pack()
            ok_button = tk.Button(self.root, text="Yay!", command=self.shop_menu)
            ok_button.pack()
        else: 
            self.youre_broke()
        
    # Displays when the user doesn't have enough money to buy something
    def youre_broke(self):
        self.clear_screen()
        messagebox.showerror(message="You don't have enough money to purchase that")
        self.shop_menu()