import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

def add_user(id, name, username):
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, name, username)
        VALUES (?, ?, ?)
    """, (id, name, username))
    conn.commit()
    print(f"Новый пользователь: {id, name, username}")

def get_all_users():
    cursor.execute("SELECT id FROM users")   
    ids = cursor.fetchall()
    return [row[0] for row in ids]