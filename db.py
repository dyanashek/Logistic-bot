import sqlite3
import logging

database = sqlite3.connect("db.db")
cursor = database.cursor()

try:
    # creates table with new users and their referrals
    cursor.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        user_id TEXT,
        user_username TEXT,
        allowed BOOLEAN DEFAULT FALSE
    )''')
except Exception as ex:
    print(ex)
    logging.error('Users table already exists.')

try:
    # creates table with new users and their referrals
    cursor.execute('''CREATE TABLE routes (
        id INTEGER PRIMARY KEY,
        unique_id TEXT,
        user_username TEXT,
        user_id TEXT,
        addresses TEXT,
        phones TEXT,
        messages TEXT,
        route INTEGER,
        status INTEGER DEFAULT 0,
        finished BOOLEAN DEFAULT FALSE
    )''')
except Exception as ex:
    logging.error(f"Can't create USERS table: {ex}")


# cursor.execute("DELETE FROM referrals WHERE id<>1000")
# database.commit()