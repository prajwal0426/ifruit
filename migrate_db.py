import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT,
    google_id TEXT,
    avatar TEXT,
    mobile TEXT,
    dob TEXT,
    address TEXT
)

            """)

conn.commit()
conn.close()
print("Database ready")