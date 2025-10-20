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
            password TEXT NOT NULL
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
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
    return redirect(url_for('login'))


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
    """Search bar"""
    query = request.args.get('q', '')
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        items = conn.execute("""
            SELECT * FROM items
            WHERE item_Name LIKE ? OR item_Brand LIKE ? OR item_Description LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    return render_template('TraderOption.html', items=items, mode='search', query=query)


# =====================
# RUN APP
# =====================
if __name__ == '__main__':
    app.run(debug=True)
