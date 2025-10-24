import sqlite3

DB_NAME = "barterzone.db"

def update_items_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        # Add item_DateBought column if it doesn't exist
        c.execute("ALTER TABLE items ADD COLUMN item_DateBought TEXT")
        print("✅ Added item_DateBought column")
    except sqlite3.OperationalError:
        print("ℹ️ item_DateBought column already exists")

    try:
        # Add item_DateOffered column if it doesn't exist
        c.execute("ALTER TABLE items ADD COLUMN item_DateOffered TEXT")
        print("✅ Added item_DateOffered column")
    except sqlite3.OperationalError:
        print("ℹ️ item_DateOffered column already exists")

    conn.commit()
    conn.close()
    print("✅ Database update completed!")

if __name__ == '__main__':
    update_items_table()