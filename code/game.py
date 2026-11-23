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
        login_label = tk.Label(self.root, text="Please input your User ID and password to login!\nOr, create a new user below")
        login_label.pack()
        userID_entry = tk.Entry(self.root)
        userID_entry.pack()
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack()
        #Checks for the UserID. If it exists, go to main menu. Else, reopen login
        login_button = tk.Button(self.root, text="Login", command=lambda: self.login_logic(userID_entry.get(), password_entry.get()))
        login_button.pack()
        register_user_button = tk.Button(self.root, text="Register a New User", command=self.register)
        register_user_button.pack()

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
        password_entry = tk.Entry(self.root, show="*")
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
        database_editor_button = tk.Button(self.root, text="Database Editor", command=self.database_editor_main_menu)
        database_editor_button.pack()
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
        join_room_label = tk.Label(self.root, text="Join Room\nEnter the room ID to join. Make sure you're connected to the same network and database\n")
        join_room_label.pack()
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

        room_name_label = tk.Label(self.root, text=self.room_name)
        room_name_label.pack()
        room_ID_label = tk.Label(self.root, text="Room ID: " + str(self.room_ID))
        room_ID_label.pack()
        IP_address_button = tk.Button(self.root, text="Show IP Address", command=self.show_IP)
        IP_address_button.pack()
        players_list = tk.Label(self.root, textvariable=current_players_list)
        players_list.pack()
        update_players_list_button = tk.Button(self.root, text="Refresh Player List", command=lambda: [current_players_list.set(setup_for_stringvar(get_all_players(self.connection, self.room_ID))), self.waiting_room_host()])
        update_players_list_button.pack()
        start_button = tk.Button(self.root, text="Start Game", command=self.start_day)
        start_button.pack()
    
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
        
        room_name_label = tk.Label(self.root, text=self.room_name)
        room_name_label.pack()
        room_ID_label = tk.Label(self.root, text="Room ID: " + str(self.room_ID))
        room_ID_label.pack()
        IP_address_button = tk.Button(self.root, text="Show IP Address", command=self.show_IP)
        IP_address_button.pack()
        waiting_button = tk.Label(self.root, text="Waiting for host to start game")
        waiting_button.pack()
        players_list = tk.Label(self.root, textvariable=current_players_list)
        players_list.pack()
        update_players_list_button = tk.Button(self.root, text="Refresh Player List", command= lambda: current_players_list.set(setup_for_stringvar(get_all_players(self.connection, self.room_ID))))
        update_players_list_button.pack()
        join_game_button = tk.Button(self.root, text="Join Game", command=self.has_game_started)
        join_game_button.pack()
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
            quit_button = tk.Button(self.root, text="Quit", command=self.quit_game)
            quit_button.pack()

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
        ingredients_forecast_frame = tk.Frame(self.root)
        ingredients_forecast_frame.pack(side="right")
        ingredients_forecast_box = tk.Label(ingredients_forecast_frame, textvariable=ingredients_forecast)
        ingredients_forecast_box.pack(fill="both")
        

        wilderness_title = tk.Label(self.root, text="Welcome to the Wilderness!\nSelect an Area!")
        wilderness_title.pack()
        areas_dropdown = tk.OptionMenu(self.root, selected_area, *unlocked_areas_list) 
        areas_dropdown.pack()
        show_forecast_button = tk.Button(self.root, text="Show area ingredient forecast", command= lambda: ingredients_forecast.set(setup_ingredients_forecast(selected_area.get(), self.connection)))
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
                campsite_label = tk.Label(self.root, text="Welcome to the campsite\nPick one of the following")
                campsite_label.pack()
                check_status_button = tk.Button(self.root, text="Check Status", command=self.check_player_status)
                check_status_button.pack()
                full_heal_button = tk.Button(self.root, text="Full Heal", command=self.full_heal_menu)
                full_heal_button.pack()
                return_inventory_button = tk.Button(self.root, text="Return ingredients to restaurant and heal 25% of your health", command=self.half_and_half)
                return_inventory_button.pack()
                return_to_restaurant_button = tk.Button(self.root, text="Return to the restaurant", command=lambda: [inv_to_database(self.connection, self.room_ID, self.local_inventory), self.restaurant_menu()])
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
        ingredients_inventory.set(print_ingredients(self.local_inventory))
        
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
        inv_to_database(self.connection, self.room_ID, self.local_inventory)
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
        # NOTE: Maybe do random messages of each type to add a little more flavor
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
        combat_buttons_frame.pack(side="bottom")
        # combat_buttons_frame.pack(side="bottom")
        
        # Displays
        player_stats_screen = tk.Label(stats_frame, textvariable=local_player_stats)
        player_stats_screen.pack(fill="both")
        enemy_stats_screen = tk.Label(stats_frame, textvariable=local_enemy_stats)
        enemy_stats_screen.pack(fill="both")
        combat_log_menu = tk.Label(combat_log_frame, textvariable=local_combat_log)
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
        orders_frame = tk.Frame(self.root)
        orders_frame.pack(side=tk.LEFT, expand=True, fill="both")
        
        ingredients_frame = tk.Frame(self.root)
        ingredients_frame.pack(side=tk.RIGHT, expand=True, fill="both")
        
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(side=tk.BOTTOM, expand=True, fill="both")
        
        # Orders GUI
        orders_interface = tk.Listbox(orders_frame, selectmode=tk.SINGLE)
        # Write a query to bring down the names of the requested orders
        orders_interface.insert(0, *self.restaurant_obj.display_customer_order_list())
        orders_interface.pack()
        
        # Ingredients Inventory GUI
        ingredients_display = tk.Label(ingredients_frame, text=f"{ingredients_list}") 
        ingredients_display.pack(side="top", expand=True, fill="both")
        
        # Buttons GUI
        back_button = tk.Button(buttons_frame, text="Back", command=self.restaurant_menu)
        back_button.pack(side=tk.LEFT, expand=True, fill="both", padx=10)
        
        # Refreshes the page
        refresh_button = tk.Button(buttons_frame, text="Refresh", command=self.cook_menu)
        refresh_button.pack(side=tk.LEFT, expand=True, fill="both", padx=10)
        cook_button = tk.Button(buttons_frame, text="Cook selected order meal", command=lambda: self.cook_order(orders_interface.curselection()[0]))
        cook_button.pack(side=tk.LEFT, expand=True, fill="both", padx=10)
    
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
        inventory_weapons_list: list[str] =  []
        weapon_stats = tk.StringVar()
        weapon_stats.set("No weapon selected to inspect")
        
        # Sets display string for current weapon
        current_weapon_stats = tk.StringVar()
        current_weapon_stats.set(self.weapon.display())
        
        self.clear_screen()
        # Setting up frames
        left_frame = tk.Frame(self.root)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        middle_frame = tk.Frame(self.root)
        middle_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        right_frame = tk.Frame(self.root)
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(side="bottom", fill="both", expand=True, padx=5, pady=5)
        
        # Setting up menus
        weapons_inventory_label = tk.Label(left_frame, text="Weapons Inventory")
        weapons_inventory_label.pack()
        weapons_inventory = tk.Listbox(left_frame, selectmode="single")
        weapons_inventory.pack()
        # Should retrieve all weapon tuples and then filter them down into a list of their names for display
        database_inventory_tuples = self.restaurant_obj.access_database_inventory_filter_type_id(2)
        
        for inventory_tuple in database_inventory_tuples:
            inventory_weapons_list.append(inventory_tuple[2])
            
        weapons_inventory.insert(0, *inventory_weapons_list)
        
        selected_weapon_compare = tk.Label(middle_frame, textvariable=weapon_stats)
        selected_weapon_compare.pack(fill="both")
        
        # Sets what weapon's stats to show in the inspector menu
        inspect_weapon_button = tk.Button(bottom_frame, text="Inspect Selected Weapon", command=lambda: weapon_stats.set(Weapon(weapons_inventory.get(weapons_inventory.curselection())).display()))
        inspect_weapon_button.pack()
        
        current_weapon_display = tk.Label(right_frame, textvariable=current_weapon_stats)
        current_weapon_display.pack(side="left", fill="both")
        
        equip_weapon_button = tk.Button(bottom_frame, text="Equip", command=lambda: self.equip_weapon(weapons_inventory.get(weapons_inventory.curselection())))
        equip_weapon_button.pack()
        
        back_button = tk.Button(bottom_frame, text="Back", command=self.equipment_menu)
        back_button.pack()
        
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
        # Setting up frames
        left_frame = tk.Frame(self.root)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        middle_frame = tk.Frame(self.root)
        middle_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        right_frame = tk.Frame(self.root)
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(side="bottom", fill="both", expand=True, padx=5, pady=5)
        
        # Setting up menus
        armor_inventory_label = tk.Label(left_frame, text="Armors Inventory")
        armor_inventory_label.pack()
        armor_inventory = tk.Listbox(left_frame, selectmode="single")
        armor_inventory.pack()
        # Should retrieve all weapon tuples and then filter them down into a list of their names for display
        database_inventory_tuples = self.restaurant_obj.access_database_inventory_filter_type_id(3)
        
        for inventory_tuple in database_inventory_tuples:
            inventory_armor_list.append(inventory_tuple[2])
            
        armor_inventory.insert(0, *inventory_armor_list)
        
        selected_armor_compare = tk.Label(middle_frame, textvariable=armor_stats)
        selected_armor_compare.pack(fill="both")
        
        # Sets what armor's stats to show in the inspector menu
        inspect_armor_button = tk.Button(bottom_frame, text="Inspect Selected Weapon", command=lambda: armor_stats.set(Armor(armor_inventory.get(armor_inventory.curselection())).display()))
        inspect_armor_button.pack()
        
        current_armor_display = tk.Label(right_frame, textvariable=current_armor_stats)
        current_armor_display.pack(side="left", fill="both")
        
        equip_armor_button = tk.Button(bottom_frame, text="Equip", command=lambda: self.equip_armor(armor_inventory.get(armor_inventory.curselection())))
        equip_armor_button.pack()
        
        back_button = tk.Button(bottom_frame, text="Back", command=self.equipment_menu)
        back_button.pack()
        
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
        restaurant_name_label = tk.Label(self.root, text=f"{self.restaurant_obj.restaurant_name}")
        restaurant_name_label.pack()
        restaurant_money_label = tk.Label(self.root, text=f"Money: {self.restaurant_obj.money}")
        restaurant_money_label.pack()
        day_label = tk.Label(self.root, text=f"Day: {self.restaurant_obj.day}")
        day_label.pack()
        player_status_label = tk.Label(self.root, text="Your character's stats:\n")
        player_status_label.pack()
        player_status = tk.StringVar()
        player_status.set(setup_for_stringvar(output_entity_stats(self.player, True)))
        weapon_info_display = tk.Label(self.root, text=f"Equipment:\n\n{self.weapon.name}:\nAttack Roll: {transform_dice_to_str(self.weapon.attack_dice)}\n Average Damage: {dice_avg(self.weapon.attack_dice)}\nAttack Modifier: {self.weapon.modifier}\nPrice: {self.weapon.price}")
        weapon_info_display.pack()
        armor_info_display = tk.Label(self.root, text=f"{self.armor.name}:\n Type: {self.armor.type}\nDefense: {self.armor.defense}\n Block Dice: {transform_dice_to_str(self.armor.block_dice)}\nDodge Dice: {transform_dice_to_str(self.armor.dodge_dice)}\nPrice: {self.armor.price}")
        armor_info_display.pack()
        ingredient_inventory_label = tk.Label(self.root, text=f"Ingredients Inventory: \n{print_ingredients_full(self.restaurant_obj.access_database_inventory_filter_type_id(1))}")
        ingredient_inventory_label.pack()
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
        # Checks to see if you have money
        if self.restaurant_obj.money >= new_weapon.price:
            self.restaurant_obj.money -= new_weapon.price
            self.restaurant_obj.update_money()
            # Pushes item to local inventory and database inventory
            self.restaurant_obj.add_item([(new_weapon.type_id, new_weapon.item_id, new_weapon.name, 1)])
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
        armors_display.insert(0, *armors_array)
    
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
            self.restaurant_obj.update_money()
            # Pushes item to local inventory and database inventory
            self.restaurant_obj.add_item([(new_armor.type_id, new_armor.item_id, new_armor.name, 1)])
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
        local_cookbooks_array: list[str] = get_cookbook_names(self.connection)
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
        displayed_cookbook: Cookbook = Cookbook(cookbook_name, self.connection)
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
            self.restaurant_obj.update_money()
            # Adds cookbook to restaurant
            self.restaurant_obj.unlock_cookbook(cookbook_obj.name)
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
        
    # Menu for ending the game
    def end_game(self):
        self.clear_screen()
        you_sure_label = tk.Label(self.root, text="Are you sure you want to end your run here?")
        you_sure_label.pack()
        yes_button = tk.Button(self.root, text="Yes", command=self.end_game_logic)
        yes_button.pack()
        no_button = tk.Button(self.root, text="No", command= self.next_day)
        no_button.pack()
        
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
            lost_label = tk.Label(self.root, text="You couldn't pay rent, or ran out of reputation this day. Your restaurant has been shut down and purchased by your mean uncle, Gustave.\n You're now unemployed. Go get a job")
            lost_label.pack()
            accept_defeat_button = tk.Button(self.root, text="Time to go back to working fast food...", command=self.quit_game)
            accept_defeat_button.pack()
            
    def next_day_non_host(self):
        self.clear_screen()
        if check_day(self.connection, self.room_ID) == -1:
            lost_label = tk.Label(self.root, text="You couldn't pay rent, or ran out of reputation this day. Your restaurant has been shut down and purchased by your mean uncle, Gustave.\n You're now unemployed. Go get a job")
            lost_label.pack()
            accept_defeat_button = tk.Button(self.root, text="Time to go back to working fast food...", command=self.quit_game)
            accept_defeat_button.pack()
        else:
            waiting_label = tk.Label(self.root, text="The day is over. Please wait for the host to start the next day")
            waiting_label.pack()
            next_day_button = tk.Button(self.root, text="Next Day", command=self.host_ready_for_next_day)
            next_day_button.pack()
            
            
    def next_day_screen(self, rent):
        self.clear_screen()
        self.restaurant_obj.update_restaurant()
        title_label = tk.Label(self.root, text=f"You're about to begin day {self.restaurant_obj.day}!")
        title_label.pack()
        rent_label = tk.Label(self.root, text=f"You paid {rent} in rent\nYou have {self.restaurant_obj.money} money left and {self.restaurant_obj.reputation} reputation")
        rent_label.pack()
        start_button = tk.Button(self.root, text="Start day!", command=self.host_ready_for_next_day)
        start_button.pack()
        if self.is_host == True:
            end_game_button = tk.Button(self.root, text="End the game", command=self.end_game)
            end_game_button.pack()
        
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
        editor_title_label = tk.Button(self.root, text="Database Editor\nSelect which category of entry you would like to add to the database")
        editor_title_label.pack()
        # Add ingredients
        add_ingredient_button = tk.Button(self.root, text="Add Ingredient", command=self.add_ingredient_menu)
        add_ingredient_button.pack()
        # Add recipes
        add_recipe_button = tk.Button(self.root, text="Add Recipe")
        add_recipe_button.pack()
        # Add cookbooks
        add_cookbook_button = tk.Button(self.root, text="Add Cookbook")
        add_cookbook_button.pack()
        # Add enemies
        add_enemy_button = tk.Button(self.root, text="Add Enemy")
        add_enemy_button.pack()
        # Add areas
        add_area_button = tk.Button(self.root, text="Add Area")
        add_area_button.pack()
        # Quit
        back_button = tk.Button(self.root, text="Back", command=self.main_menu)
        back_button.pack()
        
    # Menu for adding an ingredient
    def add_ingredient_menu(self):
        self.clear_screen()
        areas_list: list[str] = get_area_names(self.connection, self.room_ID)
        editor_title_label = tk.Button(self.root, text="Add an ingredient")
        editor_title_label.pack()
        enter_name = tk.Label(self.root, text="Ingredient name:")
        enter_name.pack()
        enter_name_entry = tk.Entry(self.root)
        enter_name_entry.pack()
        select_type_label = tk.Label(self.root, text="Select ingredient type")
        select_type_label.pack()
        select_type_entry = tk.Listbox(self.root)
        select_type_entry.pack()
        select_type_entry.insert(0, *["fish", "plant", "meat"])
        select_area_label = tk.Label(self.root, text="What area(s) should this ingredient be found in?")
        select_area_label.pack()
        select_area_dropdown = tk.Listbox(self.root, selectmode="multiple")
        select_area_dropdown.insert(0, *areas_list)
        select_area_dropdown.pack()
        
        # add_ingredient_submit = tk.Button(self.root, text="Go!", command=lambda: self.add_ingredient_weight(enter_name_entry.get(), select_type_entry.curselection(), select_area_dropdown.curselection(), areas_list, 0))
        # add_ingredient_submit.pack()
        
        
        back_button = tk.Button(self.root, text="Back", command=self.database_editor_main_menu)
        back_button.pack()
    
    # # Add weights for ingredients in different areas
    # def add_ingredient_weight(self, ingredient_name: str, ingredient_type: str, selected_area_indexes: list[int], areas_list: list[str], i: int):
    #     self.clear_screen()
    #     weight_label = tk.Label(self.root, text=f"What weight would you like this ingredient to have in {areas_list[selected_area_indexes[i]]}?")
    #     weight_label.pack()
    #     weight_entry = tk.Entry(self.root)
    #     weight_entry.pack()
    #     submit_button = tk.Button(self.root, text="Submit", command=lambda: submit_editor_ingredient(self.connection, ingredient_name=ingredient_name, ingredient_type=ingredient_type, area_name=areas_list[selected_area_indexes[i]], ingredient_weight=int(weight_entry.get())))
    #     submit_button.pack()