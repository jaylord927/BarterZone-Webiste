import sqlite3
import os

DB_NAME = "barterzone.db"


def update_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Check if columns exist and add them if they don't
    try:
        # Add full_name column if it doesn't exist
        c.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        print("✅ Added full_name column")
    except sqlite3.OperationalError:
        print("ℹ️ full_name column already exists")

    try:
        # Add contact column if it doesn't exist
        c.execute("ALTER TABLE users ADD COLUMN contact TEXT")
        print("✅ Added contact column")
    except sqlite3.OperationalError:
        print("ℹ️ contact column already exists")

    conn.commit()
    conn.close()
    print("✅ Database update completed!")


if __name__ == '__main__':
    update_database()