import sqlite3


def create_ratings_tables():
    """Create ratings and reports tables"""
    conn = sqlite3.connect('barterzone.db')
    c = conn.cursor()

    print("🔄 Creating ratings and reports tables...")

    # Ratings table
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

    # Reports table
    c.execute('''CREATE TABLE IF NOT EXISTS user_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reported_user_id INTEGER NOT NULL,
        reporting_user_id INTEGER NOT NULL,
        trade_id INTEGER NOT NULL,
        reason TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reported_user_id) REFERENCES users (id),
        FOREIGN KEY (reporting_user_id) REFERENCES users (id),
        FOREIGN KEY (trade_id) REFERENCES trades (trade_id)
    )''')

    conn.commit()
    conn.close()
    print("✅ Ratings and reports tables created successfully!")


if __name__ == '__main__':
    create_ratings_tables()