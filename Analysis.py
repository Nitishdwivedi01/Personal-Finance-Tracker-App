import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# ---------------- Database Setup ----------------
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
 
def connect_db():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysql%4012345",
        database="PFT_DB"
    )
    
# ---------------- Budget Management ----------------
def set_budget(username, month, budget_amount):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT id FROM budgets WHERE username=%s AND month=%s", (username, month))
    row = c.fetchone()
    if row:
        c.execute("UPDATE budgets SET budget_amount=%s WHERE id=%s", (budget_amount, row[0]))
    else:
        c.execute("INSERT INTO budgets (username, month, budget_amount) VALUES (%s,%s,%s)",
                  (username, month, budget_amount))
    conn.commit()
    conn.close()

def get_budget(username, month):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT budget_amount FROM budgets WHERE username=%s AND month=%s", (username, month))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def check_budget_alert(username, month):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses WHERE username=%s AND substr(date,1,7)=%s", (username, month))
    spent = c.fetchone()[0] or 0
    budget = get_budget(username, month)
    conn.close()
    if budget and spent >= budget:
        return f"⚠ Alert: You've reached or exceeded your budget of ₹{budget} for {month}!"
    elif budget:
        return f"✅ You have ₹{budget - spent:.2f} remaining for {month}."
    else:
        return "No budget set for this month."

# ---------------- Bill Reminders ----------------
def add_bill(username, bill_name, due_date, amount):
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO bills (username, bill_name, due_date, amount) VALUES (%s,%s,%s,%s)",
              (username, bill_name, due_date, amount))
    conn.commit()
    conn.close()

def upcoming_bills(username, days=7):
    conn = connect_db()
    c = conn.cursor()
    today = datetime.now().date()
    limit = today + timedelta(days=days)
    c.execute("SELECT bill_name, due_date, amount FROM bills WHERE username=%s AND status='Pending'", (username,))
    bills = []
    for name, date_str, amt in c.fetchall():
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        if today <= d <= limit:
            bills.append((name, date_str, amt))
    conn.close()
    return bills

# ---------------- Analytics ----------------
def weekly_analysis(username):
    conn = connect_db()
    c = conn.cursor()
    start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    c.execute("SELECT category, SUM(amount) FROM expenses WHERE username=%s AND date>=%s GROUP BY category",
              (username, start))
    data = c.fetchall()
    conn.close()
    return data

def monthly_analysis(username, month=None):
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses WHERE username=%s AND substr(date,1,7)=%s GROUP BY category",
              (username, month))
    data = c.fetchall()
    conn.close()
    return data

def yearly_analysis(username, year=None):
    if not year:
        year = datetime.now().strftime("%Y")
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT substr(date,6,2) AS month, SUM(amount) FROM expenses WHERE username=%s AND substr(date,1,4)=%s GROUP BY month",
              (username, year))
    data = c.fetchall()
    conn.close()
    return data

def analysis_last_n_days(username, n):
    conn = connect_db()
    c = conn.cursor()
    start = (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")
    c.execute("SELECT category, SUM(amount) FROM expenses WHERE username=%s AND date>=%s GROUP BY category",
              (username, start))
    data = c.fetchall()
    conn.close()
    return data

def income_to_expense_ratio(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses WHERE username=%s AND category LIKE '%Income%'", (username,))
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM expenses WHERE username=%s AND category NOT LIKE '%Income%'", (username,))
    expense = c.fetchone()[0] or 0
    conn.close()
    if expense == 0:
        return "N/A (No expenses)"
    ratio = income / expense if expense else 0
    return f"Income-to-Expense Ratio: {ratio:.2f}"

def balance_remaining(username):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses WHERE username=%s AND category LIKE '%Income%'", (username,))
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM expenses WHERE username=%s AND category NOT LIKE '%Income%'", (username,))
    expense = c.fetchone()[0] or 0
    conn.close()
    balance = income - expense
    return f"Balance Remaining: ₹{balance:.2f}"

def load_profile():
    pass

# Run only if script executed directly
# if __name__ == "_main_":
#     create_tables()
#     print("Database setup completed.")