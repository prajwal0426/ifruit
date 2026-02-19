import sqlite3


# Connect to database (creates file if not exists)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT,
    google_id TEXT UNIQUE,
    avatar TEXT,
    mobile TEXT,
    dob TEXT,
    address TEXT
);
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully")
  