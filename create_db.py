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
            contact TEXT
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
        # TRADE HISTORY TABLE (Optional - for tracking)
        # =====================
        c.execute('''CREATE TABLE IF NOT EXISTS trade_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id INTEGER,
            offer_user_id INTEGER,
            target_user_id INTEGER,
            offer_item_id INTEGER,
            target_item_id INTEGER,
            trade_status TEXT,
            trade_date_request TIMESTAMP,
            trade_date_completed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trade_id) REFERENCES trades (trade_id)
        )''')
        print("✅ Trade history table created")

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
        print("   - trade_history")


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


    if __name__ == '__main__':
        # Remove existing database to start fresh (optional)
        if os.path.exists('barterzone.db'):
            print("🗑️ Removing existing database...")
            os.remove('barterzone.db')

        # Create complete database
        create_complete_database()

        # Migrate any existing data
        migrate_existing_data()

        # Verify setup
        verify_database()
