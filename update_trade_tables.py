import sqlite3

DB_NAME = "barterzone.db"


def create_trade_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Trades table
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


if __name__ == '__main__':
    create_trade_tables()