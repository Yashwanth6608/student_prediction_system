from utils.db import connect_db

def register_user(username, password):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()

    conn.close()
    return user