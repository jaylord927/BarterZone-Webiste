from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

# =====================
# DATABASE SETUP
# =====================
DB_NAME = "barterzone.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
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
        conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            items_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_Name TEXT,
            item_Brand TEXT,
            item_Condition TEXT,
            item_Date TEXT,
            item_Description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """)


# Ensure DB exists
if not os.path.exists(DB_NAME):
    init_db()


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
        full_name = request.form.get('full_name', '')  # Default to empty string
        contact = request.form.get('contact', '')      # Default to empty string

        with sqlite3.connect(DB_NAME) as conn:
            try:
                conn.execute("INSERT INTO users (username, email, password, birthdate, location, full_name, contact) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (username, email, password, birthdate, location, full_name, contact))
                flash('Registration successful! You can now login.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists!', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
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
                flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """User dashboard showing all items"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        items = conn.execute("SELECT * FROM items WHERE user_id=?", (user_id,)).fetchall()
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
            request.form['item_Date'],
            request.form['item_Description']
        )

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                INSERT INTO items (user_id, item_Name, item_Brand, item_Condition, item_Date, item_Description)
                VALUES (?, ?, ?, ?, ?, ?)
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
            request.form['item_Date'],
            request.form['item_Description'],
            id,
            session['user_id']
        )

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                UPDATE items
                SET item_Name=?, item_Brand=?, item_Condition=?, item_Date=?, item_Description=?
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
    """Search bar with complete item and trader details"""
    query = request.args.get('q', '')
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        items = conn.execute("""
            SELECT i.*, u.username, u.full_name, u.location, u.contact
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE i.item_Name LIKE ? OR i.item_Brand LIKE ? OR i.item_Description LIKE ?
            OR u.username LIKE ? OR u.full_name LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()

    return render_template('search_results.html', items=items, query=query)


# NEW ROUTE: View Other Traders' Items
@app.route('/other_traders_items')
def other_traders_items():
    """View other traders' items (excluding current user's items)"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        items = conn.execute("""
            SELECT i.*, u.username, u.full_name, u.location, u.contact, u.email
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE i.user_id != ?
            ORDER BY u.username ASC
        """, (user_id,)).fetchall()

    return render_template('TraderOption.html', items=items, mode='other_traders')


# Add these new routes after your existing routes in app.py

@app.route('/request_trade', methods=['GET', 'POST'])
def request_trade():
    """Request a trade with another trader"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        target_item_id = request.form['target_item_id']
        offer_item_id = request.form['offer_item_id']

        with sqlite3.connect(DB_NAME) as conn:
            # Verify target item exists and belongs to another user
            target_item = conn.execute(
                "SELECT user_id, item_Name FROM items WHERE items_id = ?",
                (target_item_id,)
            ).fetchone()

            if not target_item:
                flash('Target item not found.', 'error')
                return redirect(url_for('other_traders_items'))

            if target_item[0] == user_id:
                flash('You cannot trade for your own item.', 'error')
                return redirect(url_for('other_traders_items'))

            # Verify offer item exists and belongs to current user
            offer_item = conn.execute(
                "SELECT item_Name FROM items WHERE items_id = ? AND user_id = ?",
                (offer_item_id, user_id)
            ).fetchone()

            if not offer_item:
                flash('You can only offer your own items.', 'error')
                return redirect(url_for('request_trade'))

            # Create trade request
            conn.execute("""
                INSERT INTO trades (offer_user_id, target_user_id, offer_item_id, target_item_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, target_item[0], offer_item_id, target_item_id))

            flash('Trade request sent successfully!', 'success')
            return redirect(url_for('view_trade_requests'))

    # GET request - show other traders' items and user's items
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        # Get other traders' items
        other_items = conn.execute("""
            SELECT i.*, u.username, u.full_name, u.location, u.contact
            FROM items i
            JOIN users u ON i.user_id = u.id
            WHERE i.user_id != ?
            ORDER BY u.username ASC
        """, (user_id,)).fetchall()

        # Get user's items for offering
        my_items = conn.execute("""
            SELECT * FROM items WHERE user_id = ?
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
        # Verify user can respond to this trade
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND target_user_id = ? AND trade_status = 'pending'",
            (trade_id, user_id)
        ).fetchone()

        if not trade:
            flash('Trade not found or you cannot respond to it.', 'error')
            return redirect(url_for('view_trade_requests'))

        if action == 'accept':
            conn.execute(
                "UPDATE trades SET trade_status = 'accepted' WHERE trade_id = ?",
                (trade_id,)
            )

            # Move to history
            trade_data = conn.execute(
                "SELECT * FROM trades WHERE trade_id = ?", (trade_id,)
            ).fetchone()

            conn.execute("""
                INSERT INTO trade_history 
                (trade_id, offer_user_id, target_user_id, offer_item_id, target_item_id, trade_status, trade_date_request)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (trade_id, trade_data[1], trade_data[2], trade_data[3], trade_data[4], 'completed', trade_data[6]))

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


# Update the trade_history route in app.py

@app.route('/trade_history')
def trade_history():
    """View trade history with receipt tracking"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        history = conn.execute("""
            SELECT t.*,
                   oi.item_Name as offer_item_name,
                   ti.item_Name as target_item_name,
                   offer_user.username as offer_username,
                   offer_user.full_name as offer_full_name,
                   target_user.username as target_username,
                   target_user.full_name as target_full_name
            FROM trades t
            LEFT JOIN items oi ON t.offer_item_id = oi.items_id
            LEFT JOIN items ti ON t.target_item_id = ti.items_id
            JOIN users offer_user ON t.offer_user_id = offer_user.id
            JOIN users target_user ON t.target_user_id = target_user.id
            WHERE (t.offer_user_id = ? OR t.target_user_id = ?) 
            AND t.trade_status IN ('accepted', 'completed')
            ORDER BY t.trade_date DESC
        """, (user_id, user_id)).fetchall()

    return render_template('trade_history.html', history=history, user_id=user_id)


@app.route('/mark_item_received/<int:trade_id>', methods=['POST'])
def mark_item_received(trade_id):
    """Mark item as received by user"""
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB_NAME) as conn:
        # Verify user is part of this trade
        trade = conn.execute(
            "SELECT * FROM trades WHERE trade_id = ? AND (offer_user_id = ? OR target_user_id = ?)",
            (trade_id, user_id, user_id)
        ).fetchone()

        if not trade:
            flash('Trade not found.', 'error')
            return redirect(url_for('trade_history'))

        # Determine which column to update
        if trade[1] == user_id:  # offer_user_id
            conn.execute(
                "UPDATE trades SET offer_received = 1 WHERE trade_id = ?",
                (trade_id,)
            )
        else:  # target_user_id
            conn.execute(
                "UPDATE trades SET target_received = 1 WHERE trade_id = ?",
                (trade_id,)
            )

        # Check if both users have received their items
        updated_trade = conn.execute(
            "SELECT offer_received, target_received FROM trades WHERE trade_id = ?",
            (trade_id,)
        ).fetchone()

        if updated_trade[0] and updated_trade[1]:
            # Both users have received items, mark trade as completed
            conn.execute(
                "UPDATE trades SET trade_status = 'completed' WHERE trade_id = ?",
                (trade_id,)
            )

        flash('Item marked as received!', 'success')

    return redirect(url_for('trade_history'))

# Add these messaging routes after your existing routes

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
# RUN APP
# =====================
if __name__ == '__main__':
    app.run(debug=True)