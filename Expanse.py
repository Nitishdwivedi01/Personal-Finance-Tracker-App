
"""Handles all database operations for the Personal Finance Tracker App."""

import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

#  MySQL connection details which the pandas will use to connect with the DB
username = "root"
password = "Mysql%254012345"
host = "localhost"
port = "3306"
db_name = "PFT_DB"

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}")

try: 
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        # print(f"Database '{db_name}' created successfully!")
finally:
    # print('Database connected')
    pass

   
def db_connect():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysql%4012345",
        database="PFT_DB"
    )


# ---------------- Expense Management ----------------
def get_user_id_name(user_unique_id):
    conn = db_connect()
    c = conn.cursor()

    c.execute(
        "SELECT User_id, username FROM users WHERE user_unique_id = %s",
        (user_unique_id,)
    )

    row = c.fetchone()
    conn.close()

    if not row:
        return None

    return {"User_id": row[0], "username": row[1]}   # integer user_id

def add_expense(user_unique_id, category, amount, date):
    User_id = get_user_id_name(user_unique_id)
    if User_id is None:
        raise ValueError("Invalid User.")
    conn = db_connect()
    c = conn.cursor()
    c.execute("INSERT INTO expenses (User_id, category, amount, date) VALUES (%s,%s,%s,%s)",
              (User_id["User_id"], category, amount, date))
    conn.commit()
    conn.close()

def add_multiple_expenses(user_unique_id, entries):
    User_id = get_user_id_name(user_unique_id)
    if User_id is None:
        raise ValueError("Invalid User.")
    
    conn = db_connect()
    c = conn.cursor()
    for e in entries:
        c.execute("INSERT INTO expenses (User_id, category, amount, date) VALUES (%s,%s,%s,%s)",
                  (User_id["User_id"], e["category"], e["amount"], e["date"]))
    conn.commit()
    conn.close()

def fetch_expenses(User_unique_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT id, category, amount, date FROM expenses WHERE User_unique_id=%s ORDER BY date DESC", (User_unique_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_expense(expense_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
    conn.commit()
    conn.close()

def edit_expense(expense_id, new_category=None, new_amount=None, new_date=None):
    conn = db_connect()
    c = conn.cursor()
    if new_category:
        c.execute("UPDATE expenses SET category=%s WHERE id=%s", (new_category, expense_id))
    if new_amount:
        c.execute("UPDATE expenses SET amount=%s WHERE id=%s", (new_amount, expense_id))
    if new_date:
        c.execute("UPDATE expenses SET date=%s WHERE id=%s", (new_date, expense_id))
    conn.commit()
    conn.close()

# ---------------- Budget Management ----------------
def set_budget(User_id, username, month, budget_amount):
   
    if User_id is None:
        raise ValueError("Invalid User.")
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT id FROM budgets WHERE user_id=%s AND month=%s", (User_id, month))

    row = c.fetchone()
    if row:
        c.execute("UPDATE budgets SET budget_amount=%s WHERE User_id=%s", (budget_amount, row[0]))
    else:
        c.execute("INSERT INTO budgets (User_id, Username, month, budget_amount) VALUES (%s,%s,%s,%s)",
                  (User_id, username, month, budget_amount))
    conn.commit()
    conn.close()

def get_budget(User_unique_id, month):  
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT budget_amount FROM budgets WHERE User_unique_id=%s AND month=%s", (User_unique_id, month))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def check_budget_alert(User_unique_id, month):
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses WHERE username=%s AND substr(date,1,7)=%s", (User_unique_id, month))
    spent = c.fetchone()[0] or 0
    budget = get_budget(User_unique_id, month)
    conn.close()
    if budget and spent >= budget:
        return f"⚠ Alert: You've reached or exceeded your budget of ₹{budget} for {month}!"
    elif budget:
        return f"✅ You have ₹{budget - spent:.2f} remaining for {month}."
    else:
        return "No budget set for this month."

# ---------------- Bill Reminders ----------------
def add_bill(User_unique_id, bill_name, due_date, amount):
    conn = db_connect()
    c = conn.cursor()
    c.execute("INSERT INTO bills (username, bill_name, due_date, amount) VALUES (%s,%s,%s,%s)",
              (User_unique_id, bill_name, due_date, amount))
    conn.commit()
    conn.close()

def upcoming_bills(User_unique_id, days=7):
    conn = db_connect()
    c = conn.cursor()
    today = datetime.now().date()
    limit = today + timedelta(days=days)
    c.execute("SELECT bill_name, due_date, amount FROM bills WHERE username=%s AND status='Pending'", (User_unique_id,))
    bills = []
    for name, date_str, amt in c.fetchall():
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        if today <= d <= limit:
            bills.append((name, date_str, amt))
    conn.close()
    return bills



