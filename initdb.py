import sqlite3

def initialize_database():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    with open('discord-bot.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)
    print("Database initialized successfully.")
    conn.close()
    
initialize_database()