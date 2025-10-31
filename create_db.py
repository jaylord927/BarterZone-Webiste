import sqlite3
import os


def create_complete_database():
    """Create complete database schema for BarterZone"""
    conn = sqlite3.connect('barterzone.db')
    c = conn.cursor()

    print("🚀 Creating complete BarterZone database...")

    # =====================
    # USERS TABLE
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            birthdate TEXT,
            location TEXT,
            full_name TEXT,
            contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    print("✅ Users table created")

    # =====================
    # ITEMS TABLE (Updated with all fields)
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS items (
            items_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_Name TEXT NOT NULL,
            item_Brand TEXT,
            item_Condition TEXT,
            item_DateBought TEXT,
            item_DateOffered TEXT,
            item_Description TEXT,
            item_image TEXT,
            item_available BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
    print("✅ Items table created")

    # =====================
    # TRADES TABLE (Complete with all columns)
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_user_id INTEGER NOT NULL,
            target_user_id INTEGER NOT NULL,
            offer_item_id INTEGER NOT NULL,
            target_item_id INTEGER NOT NULL,
            trade_status TEXT DEFAULT 'pending',
            trade_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            offer_received BOOLEAN DEFAULT 0,
            target_received BOOLEAN DEFAULT 0,
            delivery_location TEXT,
            delivery_confirmed BOOLEAN DEFAULT 0,
            meetup_location TEXT,
            meetup_gps TEXT,
            meetup_confirmed BOOLEAN DEFAULT 0,
            meetup_preferred BOOLEAN DEFAULT 0,
            meetup_date TEXT,
            meetup_time TEXT,
            delivery_preferred BOOLEAN DEFAULT 0,
            delivery_date TEXT,
            delivery_courier TEXT,
            tracking_number TEXT,
            cancellation_reason TEXT,
            FOREIGN KEY (offer_user_id) REFERENCES users (id),
            FOREIGN KEY (target_user_id) REFERENCES users (id),
            FOREIGN KEY (offer_item_id) REFERENCES items (items_id),
            FOREIGN KEY (target_item_id) REFERENCES items (items_id)
        )''')
    print("✅ Trades table created")

    # =====================
    # TRADE MESSAGES TABLE
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS trade_messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            message_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )''')
    print("✅ Trade messages table created")

    # =====================
    # TRADE ARRANGEMENTS TABLE
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS trade_arrangements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER NOT NULL,
            initiator_id INTEGER NOT NULL,
            method TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            meetup_location TEXT,
            meetup_date TEXT,
            meetup_time TEXT,
            delivery_address TEXT,
            delivery_date TEXT,
            delivery_instructions TEXT,
            courier_option TEXT,
            tracking_number TEXT,
            user1_confirmed_receipt BOOLEAN DEFAULT 0,
            user2_confirmed_receipt BOOLEAN DEFAULT 0,
            user1_confirmed_details BOOLEAN DEFAULT 0,
            user2_confirmed_details BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trade_id) REFERENCES trades (trade_id),
            FOREIGN KEY (initiator_id) REFERENCES users (id)
        )''')
    print("✅ Trade arrangements table created")

    # =====================
    # TRADE MESSAGES NEGOTIATION TABLE
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS trade_messages_negotiation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            message_type TEXT,
            content TEXT,
            suggested_location TEXT,
            suggested_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trade_id) REFERENCES trades (trade_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
    print("✅ Trade messages negotiation table created")

    # =====================
    # ADMIN TABLE (Separate from users)
    # =====================
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
    print("✅ Admin table created")

    # =====================
    # RATINGS & REPORTS TABLES
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS user_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rated_user_id INTEGER NOT NULL,
            rating_user_id INTEGER NOT NULL,
            trade_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rated_user_id) REFERENCES users (id),
            FOREIGN KEY (rating_user_id) REFERENCES users (id),
            FOREIGN KEY (trade_id) REFERENCES trades (trade_id),
            UNIQUE(rated_user_id, rating_user_id, trade_id)
        )''')
    print("✅ User ratings table created")

    c.execute('''CREATE TABLE IF NOT EXISTS user_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reported_user_id INTEGER NOT NULL,
            reporting_user_id INTEGER NOT NULL,
            trade_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            admin_notes TEXT,
            resolved_by INTEGER,
            resolved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reported_user_id) REFERENCES users (id),
            FOREIGN KEY (reporting_user_id) REFERENCES users (id),
            FOREIGN KEY (trade_id) REFERENCES trades (trade_id),
            FOREIGN KEY (resolved_by) REFERENCES users (id)
        )''')
    print("✅ User reports table created")

    # =====================
    # USER RECOMMENDATIONS TABLE
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS user_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            priority TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            contact_ok BOOLEAN DEFAULT 0,
            status TEXT DEFAULT 'pending',
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
    print("✅ User recommendations table created")

    # =====================
    # ANNOUNCEMENTS TABLE
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            priority TEXT DEFAULT 'normal',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users (id)
        )''')
    print("✅ Announcements table created")

    # =====================
    # USER BANS TABLE
    # =====================
    c.execute('''CREATE TABLE IF NOT EXISTS user_bans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            admin_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            duration_days INTEGER,
            banned_until TIMESTAMP,
            is_permanent BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (admin_id) REFERENCES users (id)
        )''')
    print("✅ User bans table created")

    conn.commit()
    conn.close()

    print("🎉 Database setup completed successfully!")
    print("📊 Tables created:")
    print("   - users")
    print("   - items")
    print("   - trades")
    print("   - trade_messages")
    print("   - trade_arrangements")
    print("   - trade_messages_negotiation")
    print("   - admin_table")
    print("   - user_ratings")
    print("   - user_reports")
    print("   - user_recommendations")
    print("   - announcements")
    print("   - user_bans")


def migrate_existing_data():
    """Migrate data from old tables if they exist"""
    conn = sqlite3.connect('barterzone.db')
    c = conn.cursor()

    try:
        # Check if old tbl_items exists and migrate data
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_items'")
        if c.fetchone():
            print("🔄 Migrating data from old tbl_items to new items table...")

            # Get old data
            c.execute("SELECT * FROM tbl_items")
            old_items = c.fetchall()

            # Insert into new table
            for item in old_items:
                c.execute('''INSERT INTO items (items_id, user_id, item_Name, item_Brand, item_Condition, 
                                item_DateBought, item_DateOffered, item_Description, item_image)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (item[0], item[6], item[1], item[2], item[3], item[4], item[4], item[5], ''))

            # Drop old table
            c.execute("DROP TABLE tbl_items")
            print("✅ Data migration completed")

    except Exception as e:
        print(f"ℹ️ No migration needed or error during migration: {e}")

    conn.commit()
    conn.close()


def verify_database():
    """Verify all tables are created correctly"""
    conn = sqlite3.connect('barterzone.db')
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()

    print("\n📋 Database verification:")
    for table in tables:
        print(f"   ✅ {table[0]}")

    conn.close()


def create_default_admin():
    """Create default admin account"""
    conn = sqlite3.connect('barterzone.db')
    c = conn.cursor()

    try:
        # Check if admin user already exists
        c.execute("SELECT id FROM users WHERE username = 'admin' OR email = 'admin@barterzone.com'")
        existing_user = c.fetchone()

        if existing_user:
            print("ℹ️ Admin user already exists")
            # Add to admin table if not already there
            c.execute("INSERT OR IGNORE INTO admin_table (user_id, username, email, full_name) VALUES (?, ?, ?, ?)",
                      (existing_user[0], 'admin', 'admin@barterzone.com', 'System Administrator'))
        else:
            # Create new admin user
            c.execute('''INSERT INTO users (username, email, password, full_name, location, contact)
                             VALUES (?, ?, ?, ?, ?, ?)''',
                      ('admin', 'admin@barterzone.com', 'admin123', 'System Administrator', 'Admin Location',
                       'Admin Contact'))

            user_id = c.lastrowid

            # Add to admin table
            c.execute('''INSERT INTO admin_table (user_id, username, email, full_name)
                             VALUES (?, ?, ?, ?)''',
                      (user_id, 'admin', 'admin@barterzone.com', 'System Administrator'))

            print("✅ Default admin user created")

        conn.commit()

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    # Remove existing database to start fresh (optional)
    if os.path.exists('barterzone.db'):
        print("🗑️ Removing existing database...")
        os.remove('barterzone.db')

    # Create complete database
    create_complete_database()

    # Migrate any existing data
    migrate_existing_data()

    # Create default admin
    create_default_admin()

    # Verify setup
    verify_database()