# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

DB = "barterzone.db"

app = Flask(__name__)
app.secret_key = "replace-with-a-random-secret"  # change in production

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM tbl_items ORDER BY item_id").fetchall()
    conn.close()
    return render_template("index.html", items=items)

@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        name = request.form.get("item_Name", "").strip()
        brand = request.form.get("item_Brand", "").strip()
        condition = request.form.get("item_Condition", "").strip()
        date_bought = request.form.get("item_Date", "").strip()
        description = request.form.get("item_Description", "").strip()

        if not name:
            flash("Item Name is required.", "error")
            return redirect(url_for("add_item"))

        # optional: validate date format YYYY-MM-DD
        if date_bought:
            try:
                datetime.strptime(date_bought, "%Y-%m-%d")
            except ValueError:
                flash("Date must be in YYYY-MM-DD format.", "error")
                return redirect(url_for("add_item"))

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO tbl_items (item_Name, item_Brand, item_Condition, item_Date, item_Description) VALUES (?, ?, ?, ?, ?)",
            (name, brand, condition, date_bought, description),
        )
        conn.commit()
        conn.close()
        flash("✅ Item offer submitted successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add_item.html")

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM tbl_items WHERE item_id = ?", (item_id,)).fetchone()
    if item is None:
        conn.close()
        flash("Item not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("item_Name", "").strip()
        brand = request.form.get("item_Brand", "").strip()
        condition = request.form.get("item_Condition", "").strip()
        date_bought = request.form.get("item_Date", "").strip()
        description = request.form.get("item_Description", "").strip()

        if not name:
            flash("Item Name is required.", "error")
            return redirect(url_for("edit_item", item_id=item_id))

        if date_bought:
            try:
                datetime.strptime(date_bought, "%Y-%m-%d")
            except ValueError:
                flash("Date must be in YYYY-MM-DD format.", "error")
                return redirect(url_for("edit_item", item_id=item_id))

        conn.execute(
            "UPDATE tbl_items SET item_Name = ?, item_Brand = ?, item_Condition = ?, item_Date = ?, item_Description = ? WHERE item_id = ?",
            (name, brand, condition, date_bought, description, item_id),
        )
        conn.commit()
        conn.close()
        flash("✅ Item updated successfully!", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_item.html", item=item)

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = get_db_connection()
    cur = conn.execute("SELECT * FROM tbl_items WHERE item_id = ?", (item_id,))
    item = cur.fetchone()
    if item:
        conn.execute("DELETE FROM tbl_items WHERE item_id = ?", (item_id,))
        conn.commit()
        flash("🗑 Item deleted successfully!", "success")
    else:
        flash("Item not found.", "error")
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
