import sqlite3


# Connect to database (creates file if not exists)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Auth
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password TEXT,
    google_id TEXT UNIQUE,

    -- Profile
    mobile TEXT,
    dob TEXT,
    address TEXT,
    avatar TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully")
  