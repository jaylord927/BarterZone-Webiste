from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ✅ Create database automatically if not exist
def init_db():
    conn = sqlite3.connect('barterzone.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tbl_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    birthdate TEXT,
                    location TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        birthdate = request.form['birthdate']
        location = request.form['location']

        conn = sqlite3.connect('barterzone.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO tbl_users (username, email, password, birthdate, location) VALUES (?, ?, ?, ?, ?)",
                      (username, email, password, birthdate, location))
            conn.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already taken. Try another one.", "error")
        conn.close()
    return render_template('register.html', title="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('barterzone.db')
        c = conn.cursor()
        c.execute("SELECT * FROM tbl_users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = user[1]
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "error")

    return render_template('login.html', title="Login")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
