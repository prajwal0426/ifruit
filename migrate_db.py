import sqlite3

DB_NAME = "database.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# -------------------------------------------------
# 1. Create users table if it does not exist
# -------------------------------------------------
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
)
""")

# -------------------------------------------------
# 2. Helper: check if column exists
# -------------------------------------------------
def column_exists(table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

# -------------------------------------------------
# 3. Add missing columns safely
# -------------------------------------------------
columns_to_add = {
    "mobile": "TEXT",
    "dob": "TEXT",
    "address": "TEXT",
    "avatar": "TEXT",
    "email": "TEXT",
    "google_id": "TEXT",
}

for column, col_type in columns_to_add.items():
    if not column_exists("users", column):
        cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {col_type}")

# -------------------------------------------------
# 4. Fix broken old users (DEV-SAFE)
# -------------------------------------------------

# Remove users with no username
cursor.execute("""
DELETE FROM users
WHERE username IS NULL OR username = ''
""")

# Assign avatar to users missing one (manual accounts only)
cursor.execute("""
UPDATE users
SET avatar = 'avatars/avatar1.png'
WHERE avatar IS NULL AND google_id IS NULL
""")

# Ensure Google users have no password
cursor.execute("""
UPDATE users
SET password = NULL
WHERE google_id IS NOT NULL
""")

conn.commit()
conn.close()

print("✅ Database migrated and cleaned successfully")