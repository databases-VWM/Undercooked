import random
import mysql.connector
import socket

#______________________________________________
# Multiplayer Connection Functions
#______________________________________________
def get_local_ip_and_port():
    with socket.socket(AF_INET, SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 53))
        s.getsockname()


#______________________________________________
# User Registration Fuctions
#______________________________________________
def generate_user_ID(connection):
    cursor = connection.cursor()
    try:
        while True:
            randomID = random.randint(1000, 9999)
            
            # Check if the ID already exists in the database
            cursor.execute(
                "SELECT 1 FROM users WHERE user_ID = %s",
                (randomID,)
            )

            # If no matching ID exists, it is available
            if cursor.fetchone() is None:
                return randomID # We can use this randomID later
            print("ID already exists, generating a new one...")

    finally:
        cursor.close()


def check_user_ID_exists(connection, user_ID):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM users WHERE user_ID = %s",
            (user_ID,)
        )


        return cursor.fetchone() is not None

    finally:
        cursor.close()

def create_new_user(connection, user_ID, username):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users VALUES (%s, %s, null)",
            (user_ID, username)
        )
        connection.commit()
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
                "SELECT 1 FROM rooms WHERE room_ID = %s",
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
            "SELECT 1 FROM rooms WHERE room_ID = %s",
            (room_ID,)
        )

        if cursor.fetchone() is None:
            print("Room does not exist.")
            return False

        # Room exists, so update the user's room_ID
        cursor.execute(
            "UPDATE users SET room_ID = %s WHERE user_ID = %s",
            (room_ID, user_ID)
        )

        connection.commit()
        return True

    finally:
        cursor.close()


def create_new_room(connection, room_ID, room_name):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO rooms VALUES (%s, %s, null)",
            (room_ID, room_name)
        )
        connection.commit()
    finally:
        cursor.close()
