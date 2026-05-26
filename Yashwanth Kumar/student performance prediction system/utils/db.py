import sqlite3

def connect_db():
    return sqlite3.connect("database.db")

def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        study_hours REAL,
        attendance REAL,
        previous_marks REAL,
        assignments REAL,
        internal_marks REAL,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()