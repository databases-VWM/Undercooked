import random
import mysql.connector

def generate_player_ID():
    randomID = None
    randomID = random.randint(1000, 9999)
    # Check if the generated ID is unique by querying the database

    
