import sqlite3

conn = sqlite3.connect('barterzone.db')
c = conn.cursor()

# Users table
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    password TEXT NOT NULL,
    birthdate TEXT,
    location TEXT
)''')

# Items table
c.execute('''CREATE TABLE IF NOT EXISTS tbl_items (
    items_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_Name TEXT NOT NULL,
    item_Brand TEXT,
    item_Condition TEXT,
    item_Date TEXT,
    item_Description TEXT,
    trader_id INTEGER,
    FOREIGN KEY (trader_id) REFERENCES users (id)
)''')

conn.commit()
conn.close()
print("✅ Database and tables ready!")
