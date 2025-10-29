import sqlite3
import os


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
        print(f"❌ Error during migration: {e}")


if __name__ == '__main__':
    add_user_specific_columns()