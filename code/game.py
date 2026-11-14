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
        root.state("zoomed" if sys.platform == "win32" else "normal")
        root.configure(bg=self.BACKGROUNDCOLOR)


        self.login()
        self.logged_in = False
        self.userID = ""
        self.room_name = ""
        self.room_ID = None
        self.player: Entity
        self.current_enemy: Entity
        # list of tuples of (ingredient, quantity)
        self.local_inventory: list[tuple[str, int]] = []
        self.current_area: Area
        self.checkpoints: dict[str, int] = {}
        self.combat_log: list[str] = []

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
        if (connect_to_room(connection, new_room_id, user_ID)):
            self.waiting_room_host()
        else:
            messagebox.showerror(message="Room not found")
            self.main_menu()

    # Logic for joining an established room
    def join_room(self, room_ID, room_IP):
        if (connect_to_room(connection, room_ID, room_IP)):
            self.waiting_room_guest()
        else:
            messagebox.showerror(message="Room not found")
            self.main_menu()

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
    def explore_node(self, checkpoint_bool = False):
        self.clear_screen()
        # Stays at same location when checkpoint is enabled
        if checkpoint_bool == False:
            self.current_area.current_node = self.current_area.current_node + 1
        # Kick back to the restaurant when done
        if self.current_area.progress == False:
            self.restaurant_menu()

        #Every time you load into a node, check for a campsite or checkpoint (5 and 10 respectively)
        #Campsite logic
        if self.current_area.current_node % 5 == 0:
            campsite_label = tk.Label(self.root, text="Welcome to the campsite\nPick one of the following")
            campsite_label.pack()
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
    
    # Sets a checkpoint for an area
    def set_checkpoint(self):
        checkpoint_message = "Your checkpoint has been set at node "
        # Regardless of whether or not the checkpoint exists, it is added or updated
        self.checkpoints[self.current_area.name] = self.current_area.current_node
        messagebox.showinfo(self.root, message=checkpoint_message+str(self.current_area.current_node))
        self.explore_node(True)
    
    # Removes a checkpoint
    def remove_checkpoint(self):
        checkpoint_message: str = "Your checkpoint has been removed in " + self.current_area.name
        self.checkpoints.pop(self.current_area.name)
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
    # TODO: Send inventory back to restaurant
    def half_and_half(self):
        self.clear_screen()
        self.local_inventory = []
        self.player.health += round(self.player.max_health * .25)
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
        # Change flavor text for elite or not
        if self.current_area.is_elite == True:
            enemy_message = "You encounter a " + self.current_area.enemy_name + "\nIt looks incredibly strong!"
        else:
            enemy_message = "While observing the landscape, a " + self.current_area.enemy_name + " appears!"
        # Actually create the enemy
        self.current_enemy = Entity(self.current_area.enemy_name)
        
        text_label = tk.Label(self.root, text=enemy_message)
        text_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.battle_menu)
        ok_button.pack()

    # Text for harvesting the node
    def harvest_node_text(self):
        self.clear_screen()
        # If player falls, skip this function
        if self.player.health <= 0:
            self.fallen_text()

        # Add ingredient to your inventory
        node_ingredient = sample_item(self.current_area.chosen_list)
        # Protects from weird edge cases
        if node_ingredient is not None:
            # Check whether the player already has this item
            item_found = False

            for i, (inventory_name, quantity) in enumerate(self.local_inventory):
                if inventory_name == node_ingredient:
                    self.local_inventory[i] = (inventory_name, quantity + 1)
                    item_found = True
                    break

            # Add a new item if it isn't already in the inventory
            if not item_found:
                self.local_inventory.append((node_ingredient, 1))
            
        text_label = tk.Label(self.root, text="You harvest the resources at this node")
        text_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.explore_node)
        ok_button.pack()

    # Text for if the character falls
    def fallen_text(self):
        self.clear_screen()
        # Removes the checkpoint in the area
        self.remove_checkpoint()
        gather_label = tk.Label(self.root, text="You run back to the restaurant injured, dropping several ingredients along the way")
        gather_label.pack()
        ok_button = tk.Button(self.root, text="Ok", command=self.restaurant_menu)
        ok_button.pack()

    # This displays the GUI for the combat
    def battle_menu(self):
        self.clear_screen()
        if (self.player.health <= 0):
            self.harvest_node_text()
        
        #TKinter variable setups
        local_combat_log = tk.StringVar()
        local_combat_log.set(setup_for_stringvar(self.combat_log))
        
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
        
        # Displays
        player_stats_screen = tk.Label(stats_frame, textvariable=local_player_stats)
        player_stats_screen.pack(fill="both")
        enemy_stats_screen = tk.Label(stats_frame, textvariable=local_enemy_stats)
        enemy_stats_screen.pack(fill="both")
        combat_log_menu = tk.Label(combat_buttons_frame, textvariable=local_combat_log)
        combat_log_menu.pack(fill="both")
        
        # Button Menu
        attack_button = tk.Button(combat_buttons_frame, text="Attack", command=lambda: [combat_attack(self.player, self.current_enemy, self.combat_log), combat_enemy_attack(self.player, self.current_enemy, log_list=self.combat_log), self.battle_menu()])
        attack_button.pack(fill="both")
        
        parry_button = tk.Button(combat_buttons_frame, text="Parry", command=lambda: [combat_parry_counter(self.player, self.current_enemy, self.combat_log), combat_enemy_attack(self.player, self.current_enemy, log_list=self.combat_log), self.battle_menu()])
        parry_button.pack(fill="both")
        
        guard_button = tk.Button(combat_buttons_frame, text="Guard", command=lambda: [combat_defend(self.player, self.combat_log), combat_enemy_attack(self.player, self.current_enemy, log_list=self.combat_log), self.battle_menu()])
        guard_button.pack(fill="both")
        
        flee_button = tk.Button(combat_buttons_frame, text="Flee(Cowardly)", command=self.wrapper_flee)
        flee_button.pack(fill="both")
        
    # Wrapper function for handling fleeing
    def wrapper_flee(self):
        successful_flee: bool = combat_flee(self.player, self.current_enemy, self.combat_log)
        if successful_flee: 
            self.restaurant_menu()
        else: 
            combat_enemy_attack(self.player, self.current_enemy, log_list=self.combat_log)
            self.battle_menu
        