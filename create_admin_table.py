import sqlite3
import os


def create_admin_table():
    """Create separate admin table and migrate existing admin users - SAFE VERSION"""
    DB_NAME = "barterzone.db"

    if not os.path.exists(DB_NAME):
        print("❌ Database file not found! Please run create_db.py first.")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    print("🔄 Creating admin table and migrating data...")

    try:
        # Create admin table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS admin_table (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        print("✅ Admin table created/verified")

        # Check if users table exists and has data
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            print("❌ Users table doesn't exist. Please run create_db.py first.")
            conn.close()
            return

        # Check if there are any users to migrate
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]

        if user_count == 0:
            print("ℹ️ No users found in database. No migration needed.")
            conn.close()
            return

        # Migrate existing admin users (using any criteria you prefer)
        # For now, let's check if there are any users that should be admins
        # You can modify this logic based on your needs

        print("ℹ️ Checking for existing admin users...")

        # Example: Make the first user an admin (you can change this logic)
        c.execute("SELECT id, username, email, full_name FROM users ORDER BY id LIMIT 1")
        first_user = c.fetchone()

        if first_user:
            user_id, username, email, full_name = first_user
            try:
                c.execute('''INSERT OR IGNORE INTO admin_table 
                            (user_id, username, email, full_name) 
                            VALUES (?, ?, ?, ?)''',
                          (user_id, username, email, full_name))
                print(f"✅ Added user '{username}' to admin table")
            except sqlite3.IntegrityError:
                print(f"ℹ️ User '{username}' is already an admin")

        # Create your specific admin account
        create_specific_admin()

        conn.commit()
        print("🎉 Admin table migration completed!")

    except Exception as e:
        print(f"❌ Error during admin table creation: {e}")

    finally:
        conn.close()


def create_specific_admin():
    """Create your specific admin account"""
    conn = sqlite3.connect('barterzone.db')
    c = conn.cursor()

    try:
        username = "jaylordbarterzone"
        email = "jblbarterzone@gmail.com"
        password = "927barterzone"
        full_name = "Jaylord BarterZone Admin"
        location = "Admin Location"
        contact = "Admin Contact"

        # Check if user already exists
        c.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = c.fetchone()

        if existing_user:
            user_id = existing_user[0]
            print(f"ℹ️ User '{username}' already exists with ID: {user_id}")
        else:
            # Create new user
            c.execute('''INSERT INTO users (username, email, password, full_name, location, contact)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (username, email, password, full_name, location, contact))
            user_id = c.lastrowid
            print(f"✅ Created new user '{username}' with ID: {user_id}")

        # Add to admin table
        try:
            c.execute('''INSERT OR IGNORE INTO admin_table 
                        (user_id, username, email, full_name) 
                        VALUES (?, ?, ?, ?)''',
                      (user_id, username, email, full_name))
            print(f"✅ Added '{username}' to admin table")
        except sqlite3.IntegrityError:
            print(f"ℹ️ '{username}' is already an admin")

        conn.commit()

    except Exception as e:
        print(f"❌ Error creating specific admin: {e}")

    finally:
        conn.close()


def add_user_specific_columns():
    """Add user-specific delivery columns to trade_arrangements table"""
    DB_NAME = "barterzone.db"

    if not os.path.exists(DB_NAME):
        print("❌ Database file not found!")
        return

    try:
        with sqlite3.connect(DB_NAME) as conn:
            # List of user-specific columns to add
            user_columns = [
                ('offer_delivery_address', 'TEXT'),
                ('target_delivery_address', 'TEXT'),
                ('offer_courier_option', 'TEXT'),
                ('target_courier_option', 'TEXT'),
                ('offer_delivery_date', 'TEXT'),
                ('target_delivery_date', 'TEXT'),
                ('offer_tracking_number', 'TEXT'),
                ('target_tracking_number', 'TEXT'),
                ('offer_delivery_instructions', 'TEXT'),
                ('target_delivery_instructions', 'TEXT')
            ]

            print("🔄 Adding user-specific columns to trade_arrangements table...")

            for column_name, column_type in user_columns:
                try:
                    # Check if column already exists
                    conn.execute(f"SELECT {column_name} FROM trade_arrangements LIMIT 1")
                    print(f"ℹ️ {column_name} column already exists")
                except sqlite3.OperationalError:
                    # Column doesn't exist, add it
                    conn.execute(f"ALTER TABLE trade_arrangements ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Added {column_name} column")

            print("🎉 User-specific columns migration completed!")

    except Exception as e:
        print(f"❌ Error during column migration: {e}")


if __name__ == '__main__':
    create_admin_table()
    add_user_specific_columns()