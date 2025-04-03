from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    
    # Create expenses table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    # Create budget table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL
        )
    """)

    # Check if budget already exists, if not insert a default budget (₹10,000)
    cursor.execute("SELECT COUNT(*) FROM budget")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO budget (amount) VALUES (10000)")

    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET"])
def index():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    if start_date and end_date:
        cursor.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ?", (start_date, end_date))
    else:
        cursor.execute("SELECT * FROM expenses")

    expenses = cursor.fetchall()

    # Get total expenses
    total_expenses = sum(float(expense[2]) for expense in expenses)

    # Get budget
    cursor.execute("SELECT amount FROM budget LIMIT 1")
    budget = cursor.fetchone()[0]  

    conn.close()

    return render_template("index.html", expenses=expenses, total_expenses=total_expenses, budget=budget)

@app.route("/add_expense", methods=["POST"])
def add_expense():
    name = request.form["name"]
    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"]

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (name, amount, category, date) VALUES (?, ?, ?, ?)", 
                   (name, amount, category, date))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/update_budget", methods=["POST"])
def update_budget():
    new_budget = request.form["budget"]

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE budget SET amount = ? WHERE id = 1", (new_budget,))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/delete_expense/<int:id>", methods=["POST"])
def delete_expense(id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
