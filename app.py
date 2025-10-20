from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "barterzone_secret"

# --- Database Helper ---
def get_db_connection():
    conn = sqlite3.connect('barterzone.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Initialize Database (run once) ---
def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password TEXT NOT NULL,
        birthdate TEXT,
        location TEXT
    )''')

    # Items table
    c.execute('''CREATE TABLE IF NOT EXISTS tbl_items (
        items_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_Name TEXT NOT NULL,
        item_Brand TEXT,
        item_Condition TEXT,
        item_Date TEXT,
        item_Description TEXT,
        trader_id INTEGER,
        FOREIGN KEY (trader_id) REFERENCES users (id)
    )''')

    conn.commit()
    conn.close()

# --- Home Page ---
@app.route('/')
def index():
    return render_template('home.html')

# --- Register ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        birthdate = request.form['birthdate']
        location = request.form['location']

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO users (username, email, password, birthdate, location)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password, birthdate, location))
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Try another.", "error")
        finally:
            conn.close()
    return render_template('register.html')

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")

    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    items = conn.execute(
        "SELECT * FROM tbl_items WHERE trader_id=?",
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('dashboard.html', items=items)

# --- Add Item ---
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['item_Name']
        brand = request.form['item_Brand']
        condition = request.form['item_Condition']
        date = request.form['item_Date']
        desc = request.form['item_Description']

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO tbl_items (item_Name, item_Brand, item_Condition, item_Date, item_Description, trader_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, brand, condition, date, desc, session['user_id']))
        conn.commit()
        conn.close()

        flash("Item added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_item.html')

# --- Edit Item ---
@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM tbl_items WHERE items_id=?", (id,)).fetchone()

    if not item:
        flash("Item not found.", "error")
        conn.close()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['item_Name']
        brand = request.form['item_Brand']
        condition = request.form['item_Condition']
        date = request.form['item_Date']
        desc = request.form['item_Description']

        conn.execute("""
            UPDATE tbl_items
            SET item_Name=?, item_Brand=?, item_Condition=?, item_Date=?, item_Description=?
            WHERE items_id=?
        """, (name, brand, condition, date, desc, id))
        conn.commit()
        conn.close()

        flash("Item updated successfully!", "success")
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit_item.html', item=item)

# --- Delete Item ---
@app.route('/delete_item/<int:id>')
def delete_item(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tbl_items WHERE items_id=?", (id,))
    conn.commit()
    conn.close()
    flash("Item deleted successfully!", "info")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
