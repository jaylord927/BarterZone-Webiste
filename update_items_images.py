import sqlite3

DB_NAME = "barterzone.db"


def add_image_column():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        # Add image column to items table
        c.execute("ALTER TABLE items ADD COLUMN item_image TEXT")
        print("✅ Added item_image column to items table")
    except sqlite3.OperationalError:
        print("ℹ️ item_image column already exists")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    add_image_column()