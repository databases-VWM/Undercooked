import random
import mysql.connector
import socket
import bcrypt
import time

#NOTE: General note for all database functions:
# Make commit statements and rollback statements and appropriate conditions

#______________________________________________
# Multiplayer Connection Functions
#______________________________________________
def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 3306))
        return s.getsockname()[0]


#______________________________________________
# User Registration Functions
#______________________________________________
def generate_user_ID(connection):
    cursor = connection.cursor()
    try:
        while True:
            randomID = random.randint(1000, 9999)
            
            # Check if the ID already exists in the database
            cursor.execute(
                "SELECT 1 FROM users WHERE user_id = %s",
                (randomID,)
            )

            # If no matching ID exists, it is available
            if cursor.fetchone() is None:
                return randomID # We can use this randomID later
            print("ID already exists, generating a new one...")

    finally:
        cursor.close()

def check_login_info(connection, user_ID, unhashed_password: str):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT password FROM users WHERE user_id = %s",
            (user_ID,)
        )

        result = cursor.fetchone()

        # User ID does not exist
        if result is None:
            return False

        # Check the provided password against the stored hash
        returned_password = result[0]

        if bcrypt.checkpw(
            unhashed_password.encode("utf-8"),
            returned_password.encode("utf-8")
        ):
            return True
        else:
            return False

    finally:
        cursor.close()



def create_new_user(connection, user_ID, username, hashed_password):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users VALUES (%s, %s, %s, False, null)",
            (user_ID, username, hashed_password)
        )
        connection.commit()
    finally:
        cursor.close()

def is_logged_in(connection, user_id):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT in_use FROM users WHERE user_id = %s",
            (user_id,)
        )

        result = cursor.fetchone()

        if result is None:
            return False

        return bool(result[0])

    finally:
        cursor.close()


def set_log_in(connection, condition: bool, user_id):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE users SET in_use = %s WHERE user_id = %s",
            (condition, user_id)
        )
    finally:
        cursor.close()


#______________________________________________
# Room Management Functions
#______________________________________________
def generate_room_ID(connection):
    cursor = connection.cursor()
    try:
        while True:
            randomID = random.randint(1000, 9999)
            
            # Check if the ID already exists in the database
            cursor.execute(
                "SELECT 1 FROM rooms WHERE room_id = %s",
                (randomID,)
            )

            # If no matching ID exists, it is available
            if cursor.fetchone() is None:
                return randomID # We can use this randomID later
            print("ID already exists, generating a new one...")
    finally:
        cursor.close()


def connect_to_room(connection, room_ID, user_ID):
    cursor = connection.cursor()

    try:
        # Check if the room exists
        cursor.execute(
            "SELECT 1 FROM rooms WHERE room_id = %s",
            (room_ID,)
        )

        if cursor.fetchone() is None:
            print("Room does not exist.")
            return False

        # Room exists, so update the user's room_ID
        cursor.execute(
            "UPDATE users SET room_id = %s WHERE user_id = %s",
            (room_ID, user_ID)
        )

        connection.commit()
        return True

    finally:
        cursor.close()
        
def get_room_name_from_ID(connection, room_ID) -> str:
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT restaurant_name FROM rooms WHERE room_id = %s",
            (room_ID, )
        )
        
        return cursor.fetchone()[0]
    finally:
        cursor.close()


def create_new_room(connection, room_ID, room_name):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO rooms VALUES (%s, %s, 1000, 0, NULL)",
            (room_ID, room_name)
        )
        connection.commit()
    finally:
        cursor.close()

# This looks for checkpoints and returns the node number if exists. If not, returns 0. 
def look_for_checkpoint(area_name: str, checkpoints: dict[str, int]) -> int:
    checkpoint_num = 0
    # This catches key errors and sets checkpoint_num equal to zero if it occurs (key not found)
    try:
        if checkpoints[area_name] != None:
            checkpoint_num = checkpoints[area_name]
    except KeyError:
        checkpoint_num = 0
    return checkpoint_num


# Takes an array and concatenates it for TKinter to use
def setup_for_stringvar(array) -> str:
    concat_str: str = ""
    for i in range(len(array)):
        if i != (len(array) - 1):
            concat_str += (array[i] + "\n")
        else:
            concat_str += (array[i])
    return concat_str


def get_all_players(connection, room_id) -> list[str]:
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT username FROM users WHERE room_id = %s",
            (room_id,)
        )

        return [row[0] for row in cursor.fetchall()]

    finally:
        cursor.close()


# Takes in a userid and returns the name
def get_username(connection, user_id) -> str:
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT username FROM users WHERE user_id = %s",
            (user_id,)
        )

        result = cursor.fetchone()

        if result is None:
            return ""

        return result[0]

    finally:
        cursor.close()

        
def increment_day(connection, room_id) -> None:
    cursor = connection.cursor()

    try:
        cursor.execute(
            "CALL increment_day(%s)",
            (room_id,)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()


def check_day(connection, room_ID) -> int:
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT game_day FROM rooms WHERE room_id = %s",
            (room_ID,)
        )

        result = cursor.fetchone()

        if result is None:
            return 0
        
        return result[0]
    
    finally:
        cursor.close()

def set_time(connection, time, room_id):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE rooms SET day_time = %s WHERE room_id = %s",
            (time, room_id)
        )
    
    finally:
        cursor.close()

def get_time(connection, room_id):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT day_time FROM rooms WHERE room_id = %s",
            (room_id,)
        )

        result = cursor.fetchone()

        if result is None:
            return ""
        
        return result[0]

    finally:
        cursor.close()