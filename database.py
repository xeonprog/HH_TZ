import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
        self.conn.commit()

    def add_user(self, user_id, name, age):
        self.c.execute("INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (user_id, name, age))
        self.conn.commit()

    def get_users(self):
        self.c.execute("SELECT * FROM users")
        return self.c.fetchall()
