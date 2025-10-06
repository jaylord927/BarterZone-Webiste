# create_db.py
import sqlite3

DB = "barterzone.db"

schema = """
CREATE TABLE IF NOT EXISTS tbl_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_Name TEXT NOT NULL,
    item_Brand TEXT,
    item_Condition TEXT,
    item_Date TEXT,
    item_Description TEXT
);
"""

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.executescript(schema)
    conn.commit()
    conn.close()
    print("Database and table created (or already existed). File:", DB)

if __name__ == "__main__":
    main()
