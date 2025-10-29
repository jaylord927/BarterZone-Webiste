from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'

# =====================
# DATABASE SETUP
# =====================
DB_NAME = "barterzone.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        # Users table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            birthdate TEXT,
            location TEXT,
            full_name TEXT,
            contact TEXT
        );
        """)

        # Items table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            items_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_Name TEXT,
            item_Brand TEXT,
            item_Condition TEXT,
            item_DateBought TEXT,
            item_DateOffered TEXT,
            item_Description TEXT,
            item_image TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """)

        # Updated Trades table with delivery/meet-up columns
        conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
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
        );
        """)

        # Trade messages table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS trade_messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            message_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        );
        """)

        conn.execute("""
               CREATE TABLE IF NOT EXISTS trade_arrangements (
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
               );
               """)

        # NEW: Trade Messages table for negotiations
        conn.execute("""
               CREATE TABLE IF NOT EXISTS trade_messages_negotiation (
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
               );
               """)


def add_user_specific_delivery_columns():
    """Add user-specific delivery columns"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            # Add user-specific delivery columns
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
                    conn.execute(f"ALTER TABLE trade_arrangements ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Added {column_name} column to trade_arrangements table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️ {column_name} column already exists")
                    else:
                        print(f"❌ Error adding {column_name}: {e}")
    except Exception as e:
        print(f"❌ Error adding user-specific columns: {e}")

def enhanced_migrate_database():
    """Enhanced database migration with user-specific delivery"""
    migrate_database()
    add_user_specific_delivery_columns()
    add_item_availability_column()

# Ensure DB exists
if not os.path.exists(DB_NAME):
    init_db()


def add_missing_columns():
    """Add missing columns to existing tables"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            # Add item_available column to items table if it doesn't exist
            try:
                conn.execute("ALTER TABLE items ADD COLUMN item_available BOOLEAN DEFAULT 1")
                print("✅ Added item_available column to items table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("ℹ️ item_available column already exists in items table")
                else:
                    print(f"❌ Error adding item_available: {e}")

            # Add other missing columns...
            print("✅ All missing columns added successfully")
    except Exception as e:
        print(f"❌ Error adding columns: {e}")

def migrate_database():
    """Comprehensive database migration with table renaming"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            # Check if old tbl_items exists and rename it
            old_table = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='tbl_items'
            """).fetchone()

            if old_table:
                print("🔄 Renaming tbl_items to items...")
                conn.execute("ALTER TABLE tbl_items RENAME TO items")
                print("✅ Successfully renamed tbl_items to items")

            # Check if items table exists, if not create it
            new_table = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='items'
            """).fetchone()

            if not new_table:
                print("🔄 Creating items table...")
                conn.execute("""
                CREATE TABLE items (
                    items_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_Name TEXT,
                    item_Brand TEXT,
                    item_Condition TEXT,
                    item_DateBought TEXT,
                    item_DateOffered TEXT,
                    item_Description TEXT,
                    item_image TEXT,
                    item_available BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """)
                print("✅ Created items table")

            # Your existing migration code continues here...
            # Add missing columns to trades table
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
                    conn.execute(f"ALTER TABLE trades ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Added {column_name} column to trades table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️ {column_name} column already exists")
                    else:
                        print(f"❌ Error adding {column_name}: {e}")

            # Check if trade_arrangements table exists
            result = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='trade_arrangements'
            """).fetchone()

            if not result:
                print("🔄 Creating new tables...")
                # Create Trade Arrangements table
                conn.execute("""
                CREATE TABLE trade_arrangements (
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
                );
                """)

                # Create Trade Messages for Negotiation table
                conn.execute("""
                CREATE TABLE trade_messages_negotiation (
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
                );
                """)
                print("✅ Created new tables")

            print("🎉 Database migration completed successfully!")
            add_missing_columns()

    except Exception as e:
        print(f"❌ Migration error: {e}")

# =====================
# ROUTES
# =====================

@app.route('/')
def index():
    """Homepage"""
    return render_template('homepage.html')


@app.route('/homepage')
def homepage():
    """Homepage alternative route"""
    return render_template('homepage.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        birthdate = request.form.get('birthdate')
        location = request.form.get('location')
        full_name = request.form.get('full_name', '')
        contact = request.form.get('contact', '')

        with sqlite3.connect(DB_NAME) as conn:
            try:
                # Check if username or email already exists
                existing_user = conn.execute(
                    "SELECT id FROM users WHERE username = ? OR email = ?",
                    (username, email)
                ).fetchone()

                if existing_user:
                    flash('Username or email already exists! Please choose different ones.', 'error')
                    return redirect(url_for('register'))

                conn.execute(
                    "INSERT INTO users (username, email, password, birthdate, location, full_name, contact) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (username, email, password, birthdate, location, full_name, contact))
                flash('Registration successful! You can now login.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username or email already exists!', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with username OR email"""
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            # Check if login is username OR email
            user = conn.execute("""
                SELECT * FROM users 
                WHERE (username = ? OR email = ?) AND password = ?
            """, (username_or_email, username_or_email, password)).fetchone()

            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                # Safely get full_name - check if the tuple has enough elements
                if len(user) > 6 and user[6]:  # Check if full_name exists and is not empty
                    session['full_name'] = user[6]
                else:
                    session['full_name'] = user[1]  # Fallback to username
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username/email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """User dashboard showing all items with proper status"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        # Get all user items with trade status information
        items = conn.execute("""
            SELECT i.*, 
                   CASE 
                       WHEN i.item_available = 0 THEN 'traded'
                       WHEN EXISTS (
                           SELECT 1 FROM trades 
                           WHERE (offer_item_id = i.items_id OR target_item_id = i.items_id)
                           AND trade_status IN ('pending', 'accepted')
                       ) THEN 'in_trade'
                       ELSE 'available'
                   END as item_status
            FROM items i 
            WHERE i.user_id = ?
        """, (user_id,)).fetchall()

    return render_template('TraderOption.html', items=items, mode='view')

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    """Add new item"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = (
            session['user_id'],
            request.form['item_Name'],
            request.form['item_Brand'],
            request.form['item_Condition'],
            request.form['item_DateBought'],  # Date bought (user input)
            request.form['item_DateOffered'],  # When offered (auto-generated)
            request.form['item_Description'],
            request.form.get('item_image', '')  # Image URL
        )

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                INSERT INTO items (user_id, item_Name, item_Brand, item_Condition, item_DateBought, item_DateOffered, item_Description, item_image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, data)

        flash('Item added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('TraderOption.html', mode='add')

@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    """Edit existing item"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        item = conn.execute("SELECT * FROM items WHERE items_id=? AND user_id=?", (id, session['user_id'])).fetchone()
        if not item:
            flash('Item not found.', 'error')
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        data = (
            request.form['item_Name'],
            request.form['item_Brand'],
            request.form['item_Condition'],
            request.form['item_DateBought'],  # Date bought
            request.form['item_DateOffered'],  # When offered
            request.form['item_Description'],
            request.form.get('item_image', ''),  # Image URL
            id,
            session['user_id']
        )

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                UPDATE items
                SET item_Name=?, item_Brand=?, item_Condition=?, item_DateBought=?, item_DateOffered=?, item_Description=?, item_image=?
                WHERE items_id=? AND user_id=?
            """, data)

        flash('Item updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('TraderOption.html', item=item, mode='edit')

@app.route('/delete_item/<int:id>')
def delete_item(id):
    """Delete an item"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM items WHERE items_id=? AND user_id=?", (id, session['user_id']))

    flash('Item deleted successfully!', 'info')
    return redirect(url_for('dashboard'))


@app.route('/search_items')
def search_items():
    """Search items - EXCLUDE ITEMS IN ACTIVE TRADES AND COMPLETED TRADES"""
    query = request.args.get('q', '')
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # EXCLUDE items that are in active trades OR completed trades
        items = conn.execute("""
            SELECT i.*, u.username, u.full_name, u.location, u.contact
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE (i.item_Name LIKE ? OR i.item_Brand LIKE ? OR i.item_Description LIKE ?
            OR u.username LIKE ? OR u.full_name LIKE ?)
            AND (i.item_available IS NULL OR i.item_available = 1)
            AND i.items_id NOT IN (
                -- Items in active trades (pending, accepted)
                SELECT offer_item_id FROM trades WHERE trade_status IN ('pending', 'accepted')
                UNION 
                SELECT target_item_id FROM trades WHERE trade_status IN ('pending', 'accepted')
                UNION
                -- Items in completed trades
                SELECT offer_item_id FROM trades WHERE trade_status = 'completed'
                UNION 
                SELECT target_item_id FROM trades WHERE trade_status = 'completed'
            )
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()

    return render_template('search_results.html', items=items, query=query)

@app.route('/other_traders_items')
def other_traders_items():
    """View other traders' items - ONLY AVAILABLE ITEMS"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Get only available items from other traders
        items = conn.execute("""
            SELECT i.*, u.username, u.full_name, u.location, u.contact
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE i.user_id != ? 
            AND i.item_available = 1
            AND i.items_id NOT IN (
                SELECT offer_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
                UNION 
                SELECT target_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
            )
            ORDER BY u.username ASC
        """, (user_id,)).fetchall()

    return render_template('TraderOption.html', items=items, mode='other_traders')

@app.route('/debug_items')
def debug_items():
    """Debug route to check items data"""
    if 'user_id' not in session:
        return "Please login first"

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        items = conn.execute("SELECT * FROM items").fetchall()

        result = "<h1>Items Debug</h1>"
        for item in items:
            result += f"""
            <div style="border:1px solid #ccc; margin:10px; padding:10px;">
                <strong>ID:</strong> {item['items_id']}<br>
                <strong>Name:</strong> {item['item_Name']}<br>
                <strong>Image URL:</strong> {item['item_image'] or 'NO IMAGE'}<br>
                <strong>Has Image:</strong> {bool(item['item_image'])}<br>
            </div>
            """
        return result

def is_item_available_for_trade(item_id):
    """Check if an item is available for trading"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Check if item exists and is available
        item = conn.execute("""
            SELECT item_available FROM items WHERE items_id = ?
        """, (item_id,)).fetchone()

        if not item or item['item_available'] == 0:
            return False

        # Check if item is involved in any active trades
        active_trade = conn.execute("""
            SELECT trade_id FROM trades 
            WHERE (offer_item_id = ? OR target_item_id = ?)
            AND trade_status IN ('pending', 'accepted')
        """, (item_id, item_id)).fetchone()

        return active_trade is None

# Add these new routes after your existing routes in app.py
@app.route('/request_trade', methods=['GET', 'POST'])
def request_trade():
    """Request a trade - ONLY SHOW AVAILABLE ITEMS"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        target_item_id = request.form['target_item_id']
        offer_item_id = request.form['offer_item_id']

        with sqlite3.connect(DB_NAME) as conn:
            # Check if target item exists and is available
            target_item = conn.execute("""
                SELECT user_id, item_Name FROM items 
                WHERE items_id = ? AND user_id != ? 
                AND item_available = 1
                AND items_id NOT IN (
                    SELECT offer_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
                    UNION 
                    SELECT target_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
                )
            """, (target_item_id, user_id)).fetchone()

            if not target_item:
                flash('Target item not found or unavailable for trading.', 'error')
                return redirect(url_for('request_trade'))

            # Check if offer item exists and is available
            offer_item = conn.execute("""
                SELECT item_Name FROM items 
                WHERE items_id = ? AND user_id = ? 
                AND item_available = 1
                AND items_id NOT IN (
                    SELECT offer_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
                    UNION 
                    SELECT target_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
                )
            """, (offer_item_id, user_id)).fetchone()

            if not offer_item:
                flash('Your offered item is unavailable for trading.', 'error')
                return redirect(url_for('request_trade'))

            # Create trade request
            conn.execute("""
                INSERT INTO trades (offer_user_id, target_user_id, offer_item_id, target_item_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, target_item[0], offer_item_id, target_item_id))

            flash('Trade request sent successfully!', 'success')
            return redirect(url_for('view_trade_requests'))

    # GET request - Show only available items
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Get other traders' available items
        other_items = conn.execute("""
            SELECT i.*, u.username, u.full_name, u.location, u.contact
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE i.user_id != ? 
            AND i.item_available = 1
            AND i.items_id NOT IN (
                SELECT offer_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
                UNION 
                SELECT target_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
            )
            ORDER BY u.username ASC
        """, (user_id,)).fetchall()

        # Get user's available items
        my_items = conn.execute("""
            SELECT * FROM items 
            WHERE user_id = ? 
            AND item_available = 1
            AND items_id NOT IN (
                SELECT offer_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
                UNION 
                SELECT target_item_id FROM trades WHERE trade_status IN ('pending', 'accepted', 'completed')
            )
        """, (user_id,)).fetchall()

    return render_template('request_trade.html',
                           other_items=other_items,
                           my_items=my_items,
                           mode='request_trade')


@app.route('/view_trade_requests')
def view_trade_requests():
    """View trade requests (incoming and outgoing)"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        trades = conn.execute("""
            SELECT t.*, 
                   oi.item_Name as offer_item_name,
                   ti.item_Name as target_item_name,
                   oi.items_id as offer_item_id,
                   ti.items_id as target_item_id,
                   offer_user.username as offer_username,
                   offer_user.full_name as offer_full_name,
                   target_user.username as target_username,
                   target_user.full_name as target_full_name,
                   CASE 
                       WHEN t.target_user_id = ? THEN 'Incoming Request'
                       WHEN t.offer_user_id = ? THEN 'Your Request'
                   END as request_type
            FROM trades t
            JOIN items oi ON t.offer_item_id = oi.items_id
            JOIN items ti ON t.target_item_id = ti.items_id
            JOIN users offer_user ON t.offer_user_id = offer_user.id
            JOIN users target_user ON t.target_user_id = target_user.id
            WHERE t.target_user_id = ? OR t.offer_user_id = ?
            ORDER BY t.trade_date DESC
        """, (user_id, user_id, user_id, user_id)).fetchall()

    return render_template('trade_requests.html', trades=trades)


@app.route('/respond_trade/<int:trade_id>', methods=['POST'])
def respond_trade(trade_id):
    """Respond to a trade request"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    action = request.form['action']

    with sqlite3.connect(DB_NAME) as conn:
        # ✅ FIX: Check if user can perform this action based on action type
        if action == 'cancel':
            # User can cancel their own pending requests (offer user)
            trade = conn.execute(
                "SELECT * FROM trades WHERE trade_id = ? AND offer_user_id = ? AND trade_status = 'pending'",
                (trade_id, user_id)
            ).fetchone()
        else:
            # For accept/decline, user must be the target user
            trade = conn.execute(
                "SELECT * FROM trades WHERE trade_id = ? AND target_user_id = ? AND trade_status = 'pending'",
                (trade_id, user_id)
            ).fetchone()

        if not trade:
            flash('Trade not found or you cannot perform this action.', 'error')
            return redirect(url_for('view_trade_requests'))

        if action == 'accept':
            conn.execute(
                "UPDATE trades SET trade_status = 'accepted' WHERE trade_id = ?",
                (trade_id,)
            )
            flash('Trade accepted successfully!', 'success')

        elif action == 'decline':
            conn.execute(
                "UPDATE trades SET trade_status = 'declined' WHERE trade_id = ?",
                (trade_id,)
            )
            flash('Trade declined.', 'info')

        elif action == 'cancel':
            conn.execute(
                "UPDATE trades SET trade_status = 'cancelled' WHERE trade_id = ?",
                (trade_id,)
            )
            flash('Trade cancelled.', 'info')

    return redirect(url_for('view_trade_requests'))


@app.route('/debug/trade/<int:trade_id>')
def debug_trade(trade_id):
    """Debug route to check trade arrangement"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        arrangement = conn.execute(
            "SELECT * FROM trade_arrangements WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

        return f"""
        <h1>Debug Trade {trade_id}</h1>
        <h2>Trade Table</h2>
        <pre>{dict(trade) if trade else 'No trade found'}</pre>
        <h2>Arrangement Table</h2>
        <pre>{dict(arrangement) if arrangement else 'No arrangement found'}</pre>
        """
        return result

@app.route('/view_item/<int:item_id>')
def view_item(item_id):
    """View single item details"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        item = conn.execute("""
            SELECT i.*, u.username, u.full_name, u.location, u.contact
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE i.items_id = ?
        """, (item_id,)).fetchone()

    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('other_traders_items'))

    return render_template('singleviewingitem.html', item=item)

@app.route('/trade_history')
def trade_history():
    """View trade history with arrangement details"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        history = conn.execute("""
            SELECT 
                t.*,
                oi.item_Name as offer_item_name,
                oi.item_image as offer_item_image,
                ti.item_Name as target_item_name, 
                ti.item_image as target_item_image,
                offer_user.username as offer_username,
                offer_user.full_name as offer_full_name,
                target_user.username as target_username,
                target_user.full_name as target_full_name,
                ta.method as arrangement_method,
                ta.status as arrangement_status,
                ta.meetup_location,
                ta.meetup_date,
                ta.meetup_time,
                ta.delivery_address,
                ta.delivery_date,
                ta.courier_option,
                ta.user1_confirmed_receipt,
                ta.user2_confirmed_receipt,
                ta.user1_confirmed_details,
                ta.user2_confirmed_details,
                ta.created_at as arrangement_created,
                ta.updated_at as arrangement_updated
            FROM trades t
            LEFT JOIN items oi ON t.offer_item_id = oi.items_id
            LEFT JOIN items ti ON t.target_item_id = ti.items_id
            JOIN users offer_user ON t.offer_user_id = offer_user.id
            JOIN users target_user ON t.target_user_id = target_user.id
            LEFT JOIN trade_arrangements ta ON t.trade_id = ta.trade_id
            WHERE (t.offer_user_id = ? OR t.target_user_id = ?) 
            AND t.trade_status IN ('accepted', 'completed')
            ORDER BY t.trade_date DESC
        """, (user_id, user_id)).fetchall()

    return render_template('trade_history.html', history=history, user_id=user_id)


@app.route('/trade/<int:trade_id>/arrangement', methods=['GET', 'POST'])
def trade_arrangement(trade_id):
    """View and update trade arrangement details"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Get trade details
        trade = conn.execute("""
            SELECT t.*, 
                   oi.item_Name as offer_item_name,
                   ti.item_Name as target_item_name,
                   offer_user.username as offer_username,
                   offer_user.full_name as offer_full_name,
                   target_user.username as target_username,
                   target_user.full_name as target_full_name
            FROM trades t
            JOIN items oi ON t.offer_item_id = oi.items_id
            JOIN items ti ON t.target_item_id = ti.items_id
            JOIN users offer_user ON t.offer_user_id = offer_user.id
            JOIN users target_user ON t.target_user_id = target_user.id
            WHERE t.trade_id = ? AND (t.offer_user_id = ? OR t.target_user_id = ?)
        """, (trade_id, user_id, user_id)).fetchone()

        if not trade:
            flash('Trade not found.', 'error')
            return redirect(url_for('view_trade_requests'))

        # Get arrangement details
        arrangement = conn.execute(
            "SELECT * FROM trade_arrangements WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

    if request.method == 'POST':
        method = request.form.get('method')

        # Get form data based on which user is submitting
        if user_id == trade['offer_user_id']:
            # Jaylord is updating his details
            delivery_address = request.form.get('offer_delivery_address')
            delivery_date = request.form.get('offer_delivery_date')
            courier_option = request.form.get('offer_courier_option')
            delivery_instructions = request.form.get('offer_delivery_instructions')
            tracking_number = request.form.get('offer_tracking_number')
        else:
            # Keth is updating her details
            delivery_address = request.form.get('target_delivery_address')
            delivery_date = request.form.get('target_delivery_date')
            courier_option = request.form.get('target_courier_option')
            delivery_instructions = request.form.get('target_delivery_instructions')
            tracking_number = request.form.get('target_tracking_number')

        with sqlite3.connect(DB_NAME) as conn:
            if not arrangement:
                # Create new arrangement
                if user_id == trade['offer_user_id']:
                    # Jaylord is creating arrangement
                    conn.execute("""
                        INSERT INTO trade_arrangements 
                        (trade_id, initiator_id, method, 
                         offer_delivery_address, offer_delivery_date, offer_courier_option, 
                         offer_delivery_instructions, offer_tracking_number,
                         user1_confirmed_details, user2_confirmed_details, user1_confirmed_receipt, user2_confirmed_receipt)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0)
                    """, (trade_id, user_id, method, delivery_address, delivery_date,
                          courier_option, delivery_instructions, tracking_number))
                else:
                    # Keth is creating arrangement
                    conn.execute("""
                        INSERT INTO trade_arrangements 
                        (trade_id, initiator_id, method, 
                         target_delivery_address, target_delivery_date, target_courier_option, 
                         target_delivery_instructions, target_tracking_number,
                         user1_confirmed_details, user2_confirmed_details, user1_confirmed_receipt, user2_confirmed_receipt)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0)
                    """, (trade_id, user_id, method, delivery_address, delivery_date,
                          courier_option, delivery_instructions, tracking_number))
            else:
                # Update existing arrangement
                if user_id == trade['offer_user_id']:
                    # Jaylord is updating his details
                    conn.execute("""
                        UPDATE trade_arrangements 
                        SET method = ?, 
                            offer_delivery_address = ?, offer_delivery_date = ?, offer_courier_option = ?, 
                            offer_delivery_instructions = ?, offer_tracking_number = ?,
                            updated_at = CURRENT_TIMESTAMP,
                            user1_confirmed_details = 0, user2_confirmed_details = 0
                        WHERE trade_id = ?
                    """, (method, delivery_address, delivery_date, courier_option,
                          delivery_instructions, tracking_number, trade_id))
                else:
                    # Keth is updating her details
                    conn.execute("""
                        UPDATE trade_arrangements 
                        SET method = ?, 
                            target_delivery_address = ?, target_delivery_date = ?, target_courier_option = ?, 
                            target_delivery_instructions = ?, target_tracking_number = ?,
                            updated_at = CURRENT_TIMESTAMP,
                            user1_confirmed_details = 0, user2_confirmed_details = 0
                        WHERE trade_id = ?
                    """, (method, delivery_address, delivery_date, courier_option,
                          delivery_instructions, tracking_number, trade_id))

            flash('Your delivery details have been updated! The other user needs to confirm the changes.', 'success')
            return redirect(url_for('trade_arrangement', trade_id=trade_id))

    # GET request - reload the arrangement data after update
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        arrangement = conn.execute(
            "SELECT * FROM trade_arrangements WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

        # Get negotiation messages
        messages = conn.execute("""
            SELECT tm.*, u.username, u.full_name
            FROM trade_messages_negotiation tm
            JOIN users u ON tm.user_id = u.id
            WHERE tm.trade_id = ?
            ORDER BY tm.created_at ASC
        """, (trade_id,)).fetchall()

    return render_template('arrangement_details.html',
                           trade=trade,
                           arrangement=arrangement,
                           messages=messages,
                           user_id=user_id)

@app.route('/trade/<int:trade_id>/cancel', methods=['POST'])
def cancel_trade_arrangement(trade_id):
    """Cancel trade from arrangement page"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        # Verify user is part of this trade
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)",
            (trade_id, user_id, user_id)
        ).fetchone()

        if not trade:
            return jsonify({'status': 'error', 'message': 'Trade not found'})

        # Cancel the trade
        conn.execute(
            "UPDATE trades SET trade_status = 'cancelled' WHERE trade_id = ?",
            (trade_id,)
        )

        # Also update arrangement status if exists
        arrangement = conn.execute(
            "SELECT * FROM trade_arrangements WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

        if arrangement:
            conn.execute(
                "UPDATE trade_arrangements SET status = 'cancelled' WHERE trade_id = ?",
                (trade_id,)
            )

        return jsonify({'status': 'success', 'message': 'Trade cancelled successfully'})

@app.route('/set_meetup_details/<int:trade_id>', methods=['POST'])
def set_meetup_details(trade_id):
    """Set or suggest meetup details"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    action = request.form['action']

    with sqlite3.connect(DB_NAME) as conn:
        # Verify user is part of this trade
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)",
            (trade_id, user_id, user_id)
        ).fetchone()

        if not trade:
            flash('Trade not found.', 'error')
            return redirect(url_for('trade_history'))

        if action == 'suggest':
            # Update meetup details
            conn.execute("""
                UPDATE trades SET 
                meetup_location = ?, meetup_date = ?, meetup_time = ?, meetup_gps = ?,
                meetup_preferred = 1, meetup_confirmed = 0
                WHERE trade_id = ?
            """, (
                request.form['meetup_location'],
                request.form.get('meetup_date'),
                request.form.get('meetup_time'),
                request.form.get('meetup_gps'),
                trade_id
            ))
            flash('Meetup details suggested! Waiting for other user to agree.', 'success')

        elif action == 'agree':
            # Agree to meetup details
            conn.execute(
                "UPDATE trades SET meetup_confirmed = 1 WHERE trade_id = ?",
                (trade_id,)
            )
            flash('You have agreed to the meetup arrangement!', 'success')

    return redirect(url_for('trade_history'))


@app.route('/set_delivery_details/<int:trade_id>', methods=['POST'])
def set_delivery_details(trade_id):
    """Set or suggest delivery details"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    action = request.form['action']

    with sqlite3.connect(DB_NAME) as conn:
        # Verify user is part of this trade
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)",
            (trade_id, user_id, user_id)
        ).fetchone()

        if not trade:
            flash('Trade not found.', 'error')
            return redirect(url_for('trade_history'))

        if action == 'suggest':
            # Update delivery details
            conn.execute("""
                UPDATE trades SET 
                delivery_location = ?, delivery_date = ?, delivery_courier = ?, tracking_number = ?,
                delivery_preferred = 1, delivery_confirmed = 0
                WHERE trade_id = ?
            """, (
                request.form['delivery_location'],
                request.form.get('delivery_date'),
                request.form.get('delivery_courier'),
                request.form.get('tracking_number'),
                trade_id
            ))
            flash('Delivery details suggested! Waiting for other user to agree.', 'success')

        elif action == 'agree':
            # Agree to delivery details
            conn.execute(
                "UPDATE trades SET delivery_confirmed = 1 WHERE trade_id = ?",
                (trade_id,)
            )
            flash('You have agreed to the delivery arrangement!', 'success')

    return redirect(url_for('trade_history'))

@app.route('/trade/<int:trade_id>/suggest_location', methods=['POST'])
def suggest_location(trade_id):
    """Suggest a location for trade arrangement"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})

    user_id = session['user_id']
    data = request.json
    location = data.get('location')

    with sqlite3.connect(DB_NAME) as conn:
        # Verify user is part of this trade
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)",
            (trade_id, user_id, user_id)
        ).fetchone()

        if not trade:
            return jsonify({'status': 'error', 'message': 'Trade not found'})

        # Create suggestion message
        conn.execute("""
            INSERT INTO trade_messages_negotiation (trade_id, user_id, message_type, content, suggested_location)
            VALUES (?, ?, 'location_suggestion', ?, ?)
        """, (trade_id, user_id, f"Suggested location: {location}", location))

        return jsonify({'status': 'success', 'message': 'Location suggestion sent'})

@app.route('/trade/<int:trade_id>/send_message', methods=['POST'])
def send_negotiation_message(trade_id):
    """Send negotiation message"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})

    user_id = session['user_id']
    message_text = request.json.get('message')

    with sqlite3.connect(DB_NAME) as conn:
        # Verify user is part of this trade
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)",
            (trade_id, user_id, user_id)
        ).fetchone()

        if not trade:
            return jsonify({'status': 'error', 'message': 'Trade not found'})

        # Save message
        conn.execute("""
            INSERT INTO trade_messages_negotiation (trade_id, user_id, message_type, content)
            VALUES (?, ?, 'text', ?)
        """, (trade_id, user_id, message_text))

        return jsonify({'status': 'success', 'message': 'Message sent'})

@app.route('/trade/<int:trade_id>/status')
def get_trade_status(trade_id):
    """Check if trade status has changed"""
    if 'user_id' not in session:
        return jsonify({'status': 'error'})

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        arrangement = conn.execute(
            "SELECT status, user1_confirmed_details, user2_confirmed_details FROM trade_arrangements WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

        # You might want to compare with previous state
        return jsonify({
            'status_changed': True,  # Implement proper comparison logic
            'current_status': arrangement['status'] if arrangement else 'pending'
        })

@app.route('/cancel_trade/<int:trade_id>', methods=['POST'])
def cancel_trade(trade_id):
    """Cancel a trade"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    reason = request.form.get('cancellation_reason', '')

    with sqlite3.connect(DB_NAME) as conn:
        # Verify user is part of this trade
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)",
            (trade_id, user_id, user_id)
        ).fetchone()

        if not trade:
            flash('Trade not found.', 'error')
            return redirect(url_for('trade_history'))

        # Cancel the trade
        conn.execute(
            "UPDATE trades SET trade_status = 'cancelled', cancellation_reason = ? WHERE trade_id = ?",
            (reason, trade_id)
        )

        flash('Trade has been cancelled.', 'info')

    return redirect(url_for('trade_history'))


@app.route('/trade/<int:trade_id>/confirm_details', methods=['POST'])
def confirm_arrangement_details(trade_id):
    """Confirm arrangement details - FIXED VERSION"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Verify user is part of this trade and get arrangement
        arrangement = conn.execute("""
            SELECT ta.*, t.offer_user_id, t.target_user_id 
            FROM trade_arrangements ta
            JOIN trades t ON ta.trade_id = t.trade_id
            WHERE ta.trade_id = ? AND (t.offer_user_id = ? OR t.target_user_id = ?)
        """, (trade_id, user_id, user_id)).fetchone()

        if not arrangement:
            return jsonify({'status': 'error', 'message': 'Arrangement not found'})

        # Determine which user is confirming
        if user_id == arrangement['offer_user_id']:
            conn.execute(
                "UPDATE trade_arrangements SET user1_confirmed_details = 1 WHERE trade_id = ?",
                (trade_id,)
            )
            user_role = "offer user"
        else:
            conn.execute(
                "UPDATE trade_arrangements SET user2_confirmed_details = 1 WHERE trade_id = ?",
                (trade_id,)
            )
            user_role = "target user"

        # Check if both confirmed
        updated_arrangement = conn.execute(
            "SELECT user1_confirmed_details, user2_confirmed_details, status FROM trade_arrangements WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

        if updated_arrangement['user1_confirmed_details'] and updated_arrangement['user2_confirmed_details']:
            # Both users confirmed - update status to accepted
            conn.execute(
                "UPDATE trade_arrangements SET status = 'accepted' WHERE trade_id = ?",
                (trade_id,)
            )
            # Also update the main trade status
            conn.execute(
                "UPDATE trades SET trade_status = 'accepted' WHERE trade_id = ?",
                (trade_id,)
            )
            arrangement_status = 'accepted'
            message = '🎉 Both users have confirmed! Trade is now accepted and ready for exchange.'
        else:
            arrangement_status = 'pending'
            message = '✅ Your confirmation has been recorded. Waiting for other user to confirm.'

        conn.commit()

        return jsonify({
            'status': 'success',
            'message': message,
            'arrangement_status': arrangement_status,
            'user_confirmed': user_role,
            'user1_confirmed': bool(updated_arrangement['user1_confirmed_details']),
            'user2_confirmed': bool(updated_arrangement['user2_confirmed_details'])
        })

@app.route('/confirm_meetup_location/<int:trade_id>')
def confirm_meetup_location(trade_id):
    """Confirm meet-up location"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        # Verify user can confirm (should be the other party)
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND offer_user_id = ?",
            (trade_id, user_id)
        ).fetchone()

        if not trade:
            flash('You cannot confirm this location.', 'error')
            return redirect(url_for('trade_history'))

        conn.execute(
            "UPDATE trades SET meetup_confirmed = 1 WHERE trade_id = ?",
            (trade_id,)
        )

        flash('Meet-up location confirmed!', 'success')

    return redirect(url_for('trade_history'))


@app.route('/mark_item_received/<int:trade_id>', methods=['POST'])
def mark_item_received(trade_id):
    """Mark item as received from trade history - MARK ITEMS AS UNAVAILABLE"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Get trade details
        trade = conn.execute("""
            SELECT * FROM trades 
            WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)
        """, (trade_id, user_id, user_id)).fetchone()

        if not trade:
            flash('Trade not found.', 'error')
            return redirect(url_for('trade_history'))

        # Mark item as received in BOTH tables
        if trade['offer_user_id'] == user_id:
            # User is the offer user - mark their received item
            conn.execute(
                "UPDATE trades SET offer_received = 1 WHERE trade_id = ?",
                (trade_id,)
            )
            flash('You marked your received item!', 'success')
        else:
            # User is the target user - mark their received item
            conn.execute(
                "UPDATE trades SET target_received = 1 WHERE trade_id = ?",
                (trade_id,)
            )
            flash('You marked your received item!', 'success')

        # Check if both users have received items
        updated_trade = conn.execute(
            "SELECT offer_received, target_received FROM trades WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

        # MARK ITEMS AS UNAVAILABLE WHEN TRADE IS COMPLETED
        if updated_trade['offer_received'] and updated_trade['target_received']:
            # Both users have received items - mark trade as completed
            conn.execute(
                "UPDATE trades SET trade_status = 'completed' WHERE trade_id = ?",
                (trade_id,)
            )

            # MARK BOTH ITEMS AS UNAVAILABLE - VERY IMPORTANT!
            conn.execute(
                "UPDATE items SET item_available = 0 WHERE items_id = ?",
                (trade['offer_item_id'],)
            )
            conn.execute(
                "UPDATE items SET item_available = 0 WHERE items_id = ?",
                (trade['target_item_id'],)
            )

            flash('🎉 Trade completed! Both items received and marked as unavailable for future trades.', 'success')

    return redirect(url_for('trade_history'))

@app.route('/trade/<int:trade_id>/confirm_receipt', methods=['POST'])
def confirm_item_receipt(trade_id):
    """Mark item as received in unified system - DEBUG VERSION"""
    print(f"DEBUG: confirm_receipt called for trade {trade_id}")

    if 'user_id' not in session:
        print("DEBUG: User not logged in")
        return jsonify({'status': 'error', 'message': 'Please login first'})

    user_id = session['user_id']
    print(f"DEBUG: User ID: {user_id}")

    # Get JSON data properly
    if request.is_json:
        data = request.get_json()
        tracking_number = data.get('tracking_number', '') if data else ''
    else:
        tracking_number = ''

    print(f"DEBUG: Tracking number: {tracking_number}")

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row

            # Verify user is part of this trade and get arrangement
            arrangement = conn.execute("""
                SELECT ta.*, t.offer_user_id, t.target_user_id 
                FROM trade_arrangements ta
                JOIN trades t ON ta.trade_id = t.trade_id
                WHERE ta.trade_id = ? AND (t.offer_user_id = ? OR t.target_user_id = ?)
            """, (trade_id, user_id, user_id)).fetchone()

            if not arrangement:
                print("DEBUG: Arrangement not found")
                return jsonify({'status': 'error', 'message': 'Arrangement not found'})

            print(
                f"DEBUG: Found arrangement - User1: {arrangement['offer_user_id']}, User2: {arrangement['target_user_id']}")

            # Determine which user is marking received
            if user_id == arrangement['offer_user_id']:
                print("DEBUG: User is offer_user - marking user1_confirmed_receipt")
                conn.execute(
                    "UPDATE trade_arrangements SET user1_confirmed_receipt = 1 WHERE trade_id = ?",
                    (trade_id,)
                )
                # Also update the trades table
                conn.execute(
                    "UPDATE trades SET offer_received = 1 WHERE trade_id = ?",
                    (trade_id,)
                )
                user_role = "offer user"
            else:
                print("DEBUG: User is target_user - marking user2_confirmed_receipt")
                conn.execute(
                    "UPDATE trade_arrangements SET user2_confirmed_receipt = 1 WHERE trade_id = ?",
                    (trade_id,)
                )
                # Also update the trades table
                conn.execute(
                    "UPDATE trades SET target_received = 1 WHERE trade_id = ?",
                    (trade_id,)
                )
                user_role = "target user"

            # Update tracking number if provided
            if tracking_number:
                print(f"DEBUG: Updating tracking number: {tracking_number}")
                conn.execute(
                    "UPDATE trade_arrangements SET tracking_number = ? WHERE trade_id = ?",
                    (tracking_number, trade_id)
                )

            # Check if both received
            updated_arrangement = conn.execute(
                "SELECT user1_confirmed_receipt, user2_confirmed_receipt FROM trade_arrangements WHERE trade_id = ?",
                (trade_id,)
            ).fetchone()

            print(
                f"DEBUG: After update - User1 received: {updated_arrangement['user1_confirmed_receipt']}, User2 received: {updated_arrangement['user2_confirmed_receipt']}")

            if updated_arrangement['user1_confirmed_receipt'] and updated_arrangement['user2_confirmed_receipt']:
                print("DEBUG: Both users confirmed receipt - marking as completed")
                conn.execute(
                    "UPDATE trade_arrangements SET status = 'completed' WHERE trade_id = ?",
                    (trade_id,)
                )
                # Also update the main trade status
                conn.execute(
                    "UPDATE trades SET trade_status = 'completed' WHERE trade_id = ?",
                    (trade_id,)
                )
                conn.commit()
                return jsonify(
                    {'status': 'completed', 'message': '🎉 Both items received! Trade completed successfully.'})
            else:
                conn.commit()
                return jsonify({'status': 'waiting',
                                'message': f'✅ You marked your item as received! Waiting for other user to confirm.'})

    except Exception as e:
        print(f"DEBUG: Error occurred: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Database error: {str(e)}'})

@app.route('/trade/<int:trade_id>/complete_trade', methods=['POST'])
def complete_trade(trade_id):
    """Complete trade and mark items as unavailable"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})

    user_id = session['user_id']

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row

            # Get trade details
            trade = conn.execute("""
                SELECT * FROM trades WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)
            """, (trade_id, user_id, user_id)).fetchone()

            if not trade:
                return jsonify({'status': 'error', 'message': 'Trade not found'})

            # Mark items as unavailable
            conn.execute("UPDATE items SET item_available = 0 WHERE items_id = ?", (trade['offer_item_id'],))
            conn.execute("UPDATE items SET item_available = 0 WHERE items_id = ?", (trade['target_item_id'],))

            # Update trade status to completed
            conn.execute("UPDATE trades SET trade_status = 'completed' WHERE trade_id = ?", (trade_id,))

            # Update arrangement status
            conn.execute("UPDATE trade_arrangements SET status = 'completed' WHERE trade_id = ?", (trade_id,))

            return jsonify({'status': 'success', 'message': 'Trade completed successfully! Items marked as unavailable.'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error completing trade: {str(e)}'})

@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    """Send message to another trader"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        receiver_id = request.form['receiver_id']
        message_text = request.form['message_text']

        if not message_text.strip():
            flash('Message cannot be empty.', 'error')
            return redirect(url_for('send_message'))

        with sqlite3.connect(DB_NAME) as conn:
            # Verify receiver exists and is not the current user
            receiver = conn.execute(
                "SELECT id FROM users WHERE id = ? AND id != ?",
                (receiver_id, user_id)
            ).fetchone()

            if not receiver:
                flash('Invalid trader selected.', 'error')
                return redirect(url_for('send_message'))

            # Send message
            conn.execute("""
                INSERT INTO trade_messages (sender_id, receiver_id, message_text)
                VALUES (?, ?, ?)
            """, (user_id, receiver_id, message_text))

            flash('Message sent successfully!', 'success')
            return redirect(url_for('view_messages'))

    # GET request - show list of traders
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        traders = conn.execute("""
            SELECT id, username, full_name, location, contact 
            FROM users 
            WHERE id != ?
            ORDER BY username ASC
        """, (user_id,)).fetchall()

    return render_template('send_message.html', traders=traders)


@app.route('/view_messages')
def view_messages():
    """View message conversations"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Get list of traders the user has chatted with
        chat_partners = conn.execute("""
            SELECT DISTINCT 
                CASE 
                    WHEN sender_id = ? THEN receiver_id 
                    ELSE sender_id 
                END AS partner_id,
                u.username,
                u.full_name
            FROM trade_messages m
            JOIN users u ON u.id = CASE 
                WHEN m.sender_id = ? THEN m.receiver_id 
                ELSE m.sender_id 
            END
            WHERE sender_id = ? OR receiver_id = ?
            ORDER BY u.username ASC
        """, (user_id, user_id, user_id, user_id)).fetchall()

    return render_template('view_messages.html', chat_partners=chat_partners)


@app.route('/chat/<int:partner_id>', methods=['GET', 'POST'])
def chat(partner_id):
    """View and send messages in a chat"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        message_text = request.form['message_text']

        if not message_text.strip():
            flash('Message cannot be empty.', 'error')
            return redirect(url_for('chat', partner_id=partner_id))

        with sqlite3.connect(DB_NAME) as conn:
            # Verify partner exists
            partner = conn.execute(
                "SELECT id FROM users WHERE id = ? AND id != ?",
                (partner_id, user_id)
            ).fetchone()

            if not partner:
                flash('Invalid trader.', 'error')
                return redirect(url_for('view_messages'))

            # Send message
            conn.execute("""
                INSERT INTO trade_messages (sender_id, receiver_id, message_text)
                VALUES (?, ?, ?)
            """, (user_id, partner_id, message_text))

            return redirect(url_for('chat', partner_id=partner_id))

    # GET request - show chat history
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Get partner info
        partner = conn.execute(
            "SELECT username, full_name FROM users WHERE id = ?",
            (partner_id,)
        ).fetchone()

        if not partner:
            flash('Trader not found.', 'error')
            return redirect(url_for('view_messages'))

        # Get chat history
        messages = conn.execute("""
            SELECT m.*, 
                   sender.username as sender_username,
                   sender.full_name as sender_full_name,
                   receiver.username as receiver_username
            FROM trade_messages m
            JOIN users sender ON m.sender_id = sender.id
            JOIN users receiver ON m.receiver_id = receiver.id
            WHERE (m.sender_id = ? AND m.receiver_id = ?) 
               OR (m.sender_id = ? AND m.receiver_id = ?)
            ORDER BY m.message_date ASC
        """, (user_id, partner_id, partner_id, user_id)).fetchall()

    return render_template('chat.html',
                           messages=messages,
                           partner=partner,
                           partner_id=partner_id,
                           user_id=user_id)


# Add these profile routes after your existing routes

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile page - view and update profile"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        full_name = request.form['full_name']
        contact = request.form['contact']
        birthdate = request.form['birthdate']
        location = request.form['location']

        # Check if password is being updated
        new_password = request.form.get('new_password')

        with sqlite3.connect(DB_NAME) as conn:
            try:
                if new_password:
                    # Update with new password
                    conn.execute("""
                        UPDATE users 
                        SET username=?, email=?, password=?, full_name=?, contact=?, birthdate=?, location=?
                        WHERE id=?
                    """, (username, email, new_password, full_name, contact, birthdate, location, user_id))
                    flash('Profile and password updated successfully!', 'success')
                else:
                    # Update without changing password
                    conn.execute("""
                        UPDATE users 
                        SET username=?, email=?, full_name=?, contact=?, birthdate=?, location=?
                        WHERE id=?
                    """, (username, email, full_name, contact, birthdate, location, user_id))
                    flash('Profile updated successfully!', 'success')

                # Update session data
                session['username'] = username
                if full_name:
                    session['full_name'] = full_name

            except sqlite3.IntegrityError:
                flash('Username already exists! Please choose a different one.', 'error')
                return redirect(url_for('profile'))

    # GET request - load current user data
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    return render_template('profile.html', user=user)


@app.route('/change_password', methods=['POST'])
def change_password():
    """Change password only"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        flash('New passwords do not match!', 'error')
        return redirect(url_for('profile'))

    with sqlite3.connect(DB_NAME) as conn:
        # Verify current password
        user = conn.execute(
            "SELECT password FROM users WHERE id = ? AND password = ?",
            (user_id, current_password)
        ).fetchone()

        if not user:
            flash('Current password is incorrect!', 'error')
            return redirect(url_for('profile'))

        # Update password
        conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (new_password, user_id)
        )

    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))

# =====================
# HELPER FUNCTIONS
# =====================

def update_item_availability(item_id, available=True):
    """Update item availability status"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE items SET item_available = ? WHERE items_id = ?",
            (1 if available else 0, item_id)
        )

def get_item_availability(item_id):
    """Check if item is available for trading"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        item = conn.execute(
            "SELECT item_available FROM items WHERE items_id = ?",
            (item_id,)
        ).fetchone()
        return item['item_available'] if item else False

# Update the items table to include availability column
# Add this to your app.py or run as a separate script
def add_item_availability_column():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("ALTER TABLE items ADD COLUMN item_available BOOLEAN DEFAULT 1")
            print("✅ Added item_available column to items table")

            # Set all existing items as available
            conn.execute("UPDATE items SET item_available = 1 WHERE item_available IS NULL")
            print("✅ Set all existing items as available")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ item_available column already exists")
        else:
            print(f"❌ Error adding item_available: {e}")


# Call this in your migrate_database function
def enhanced_migrate_database():
    """Enhanced database migration with item availability"""
    migrate_database()  # Your existing migration
    add_item_availability_column()

# =====================
# RUN APP
# =====================
if __name__ == '__main__':
    app.run(debug=True)