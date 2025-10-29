import sqlite3


def fix_database():
    """Quick fix for missing columns"""
    conn = sqlite3.connect('barterzone.db')
    c = conn.cursor()

    try:
        # Add item_available column if it doesn't exist
        c.execute("ALTER TABLE items ADD COLUMN item_available BOOLEAN DEFAULT 1")
        print("✅ Added item_available column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ item_available column already exists")
        else:
            print(f"❌ Error: {e}")

    conn.commit()
    conn.close()
    print("🎉 Database fix completed!")


if __name__ == '__main__':
    fix_database()