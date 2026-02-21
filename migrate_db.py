import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Add columns safely
try:
    cursor.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN dob TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT")
except:
    pass

conn.commit()
conn.close()

print("Database migrated successfully")