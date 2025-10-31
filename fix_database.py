import sqlite3
import os


def fix_database():
    """Comprehensive database fixes"""
    DB_NAME = "barterzone.db"

    if not os.path.exists(DB_NAME):
        print("❌ Database file not found! Please run create_db.py first.")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    print("🔧 Running comprehensive database fixes...")

    try:
        # 1. Add item_available column if it doesn't exist
        try:
            c.execute("ALTER TABLE items ADD COLUMN item_available BOOLEAN DEFAULT 1")
            print("✅ Added item_available column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️ item_available column already exists")
            else:
                print(f"❌ Error adding item_available: {e}")

        # 2. Set all existing items as available
        c.execute("UPDATE items SET item_available = 1 WHERE item_available IS NULL")
        print("✅ Set all existing items as available")

        # 3. Add missing columns to trades table
        missing_columns = [
            ('meetup_preferred', 'BOOLEAN DEFAULT 0'),
            ('meetup_date', 'TEXT'),
            ('meetup_time', 'TEXT'),
            ('delivery_preferred', 'BOOLEAN DEFAULT 0'),
            ('delivery_date', 'TEXT'),
            ('delivery_courier', 'TEXT'),
            ('tracking_number', 'TEXT'),
            ('cancellation_reason', 'TEXT')
        ]

        for column_name, column_type in missing_columns:
            try:
                c.execute(f"ALTER TABLE trades ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added {column_name} column to trades table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"ℹ️ {column_name} column already exists")
                else:
                    print(f"❌ Error adding {column_name}: {e}")

        # 4. Add user-specific columns to trade_arrangements
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

        for column_name, column_type in user_columns:
            try:
                c.execute(f"ALTER TABLE trade_arrangements ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added {column_name} column to trade_arrangements")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"ℹ️ {column_name} column already exists")
                else:
                    print(f"❌ Error adding {column_name}: {e}")

        conn.commit()
        print("🎉 Database fixes completed successfully!")

    except Exception as e:
        print(f"❌ Error during database fixes: {e}")

    finally:
        conn.close()


def verify_fixes():
    """Verify all fixes were applied correctly"""
    DB_NAME = "barterzone.db"

    if not os.path.exists(DB_NAME):
        print("❌ Database file not found!")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    print("\n🔍 Verifying database fixes...")

    try:
        # Check item_available column
        c.execute("PRAGMA table_info(items)")
        columns = [col[1] for col in c.fetchall()]
        if 'item_available' in columns:
            print("✅ item_available column: PRESENT")
        else:
            print("❌ item_available column: MISSING")

        # Check user-specific columns in trade_arrangements
        c.execute("PRAGMA table_info(trade_arrangements)")
        arrangement_columns = [col[1] for col in c.fetchall()]

        user_columns = [
            'offer_delivery_address', 'target_delivery_address',
            'offer_courier_option', 'target_courier_option',
            'offer_delivery_date', 'target_delivery_date',
            'offer_tracking_number', 'target_tracking_number',
            'offer_delivery_instructions', 'target_delivery_instructions'
        ]

        for col in user_columns:
            if col in arrangement_columns:
                print(f"✅ {col}: PRESENT")
            else:
                print(f"❌ {col}: MISSING")

    except Exception as e:
        print(f"❌ Error during verification: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    fix_database()
    verify_fixes()