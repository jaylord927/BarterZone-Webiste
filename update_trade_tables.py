import sqlite3

DB_NAME = "barterzone.db"


def create_trade_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Trades table with delivery/meet-up columns
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
        FOREIGN KEY (offer_user_id) REFERENCES users (id),
        FOREIGN KEY (target_user_id) REFERENCES users (id),
        FOREIGN KEY (offer_item_id) REFERENCES items (items_id),
        FOREIGN KEY (target_item_id) REFERENCES items (items_id)
    )''')

    # Trade messages table
    c.execute('''CREATE TABLE IF NOT EXISTS trade_messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_id INTEGER,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        message_text TEXT NOT NULL,
        message_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (trade_id) REFERENCES trades (trade_id),
        FOREIGN KEY (sender_id) REFERENCES users (id),
        FOREIGN KEY (receiver_id) REFERENCES users (id)
    )''')

    # Trade history table
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

    conn.commit()
    conn.close()
    print("✅ Trade tables created successfully!")


def add_delivery_meetup_columns():
    """Add delivery and meet-up columns to existing trades table"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # List of columns to add
    columns_to_add = [
        ('delivery_location', 'TEXT'),
        ('delivery_confirmed', 'BOOLEAN DEFAULT 0'),
        ('meetup_location', 'TEXT'),
        ('meetup_gps', 'TEXT'),
        ('meetup_confirmed', 'BOOLEAN DEFAULT 0')
    ]

    # Check if columns exist and add them if they don't
    for column_name, column_type in columns_to_add:
        try:
            c.execute(f"ALTER TABLE trades ADD COLUMN {column_name} {column_type}")
            print(f"✅ Added {column_name} column to trades table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"ℹ️ {column_name} column already exists")
            else:
                print(f"❌ Error adding {column_name}: {e}")

    conn.commit()
    conn.close()
    print("✅ Database update completed!")


if __name__ == '__main__':
    create_trade_tables()
    add_delivery_meetup_columns()