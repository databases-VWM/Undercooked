import random
import mysql.connector

def generate_player_ID(connection):
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


def check_player_ID_exists(connection, player_ID, flag):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM users WHERE user_ID = %s LIMIT 1",
            (player_ID,)
        )

        flag = cursor.fetchone() is not None

    finally:
        cursor.close()

def create_new_player(connection, player_ID, username):
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users VALUES (%s, %s, null)",
            (player_ID, username)
        )
        connection.commit()
    finally:
        cursor.close()