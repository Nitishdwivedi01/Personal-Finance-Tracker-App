# Importing the required libraries

from logging import root
from tkinter import messagebox
import pandas as pd
import re
import random
import mysql.connector
from sqlalchemy import create_engine, text


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
        print(f"Database '{db_name}' created successfully!")
finally:
    print('Database connected')

   
def db_connect():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysql%4012345",
        database="PFT_DB"
    )
    
def create_tables():
    conn = db_connect()
    c = conn.cursor()

    # User Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        User_id INT AUTO_INCREMENT PRIMARY KEY,
        First_name VARCHAR(50),
        Last_name VARCHAR(50),
        Username VARCHAR(101) AS (CONCAT(First_name, ' ', Last_name)) VIRTUAL UNIQUE,
        User_pass VARCHAR(50),
        Pin VARCHAR(10) UNIQUE,
        User_unique_id VARCHAR(50) UNIQUE,
        Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        User_id INT NOT NULL,
        Category VARCHAR(50),
        Amount DECIMAL(10,2),
        Date DATE,
        FOREIGN KEY(User_id) REFERENCES users(User_id)
        )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        User_id INT NOT NULL,
        User_unique_id VARCHAR(50),
        Month VARCHAR(20),
        Budget_amount DECIMAL(10,2),
        FOREIGN KEY(User_id) REFERENCES users(User_id)
        )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        User_id INT NOT NULL,
        Username VARCHAR(50),
        Bill_name VARCHAR(50),
        Due_date DATE,
        Amount DECIMAL(10,2),
        Status VARCHAR(20) DEFAULT 'Pending',
        FOREIGN KEY(User_id) REFERENCES users(User_id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("Tables created successfully!")
    
    
# ---------------- Authentication ----------------
def register_user(first_name, last_name, user_pass):
    conn = db_connect()
    c = conn.cursor()
    first_name = first_name.upper().strip()
    last_name = last_name.upper().strip()
    username = f"{first_name} {last_name}".strip()
    
    # Generate unique username
    user_base_name = str(f"{first_name}.{last_name}").strip()
    user_suffix = (str("/") +str(random.randint(100, 999)).strip()).strip()
    user_unique_id = user_base_name + user_suffix
    # user_unique_id = username
    
    # Check if username exists
    c.execute("SELECT username, user_unique_id FROM users WHERE username=%s OR user_unique_id=%s", (username, user_unique_id))
    if c.fetchone():
        conn.close()
        return False, "Username already exists."
    
    #Generating unique 4-digit PIN
    pin = str(random.randint(1000, 9999))
    
    # Original password stored for recovery purposes
    c.execute("INSERT INTO users (first_name, last_name, user_pass, pin,user_unique_id) VALUES (%s,%s,%s,%s,%s)",
              (first_name, last_name,user_pass, pin, user_unique_id))
    conn.commit()
    conn.close()    
    return True,f"""
        f"🎉 Registration Successful!\n"
        f"👤 Username: {username}\n"
        f"🆔 Unique ID: {user_unique_id}\n"
        f"🔐 PIN: {pin}"
    """

def login_user(user_unique_id, user_pass= None, pin= None): # Login with either password or PIN, but i was unable to make it work with both
    conn = db_connect()
    c = conn.cursor()

    if user_pass is not None and user_pass != "":
        c.execute("SELECT User_id, user_pass, username FROM users WHERE user_unique_id=%s", (user_unique_id,))
        row = c.fetchone()
        
        if not row:
                return False, "User not found, incorrect Username or password."
        if row[1] == user_pass:
            return True, f"Login successful, Welcome {row[2]}!"
        else:
            conn.close()
            return False, "Incorrect Password/PIN."
    
    # elif pin is not None and pin != "":
    #     c.execute("SELECT User_id, pin, username FROM users WHERE user_unique_id=%s", (user_unique_id,))

    #     row = c.fetchone()

    #     if not row:
    #         return False, "User not found, incorrect Username or password."
    #     if row[1] == pin:
    #         return True, f"Welcome {row[2]}!"
    
    #     else:
    #         conn.close()
    #         return False, "Incorrect Password/PIN."


def login_with_pin(user_unique_id, pin): # Login with PIN only based on same as above functionality and structure
    conn = db_connect()
    c = conn.cursor()

    c.execute("SELECT pin, username FROM users WHERE user_unique_id=%s", (user_unique_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False, "User not found, incorrect Username or PIN."
    if row[0] == pin:
        return True, f"Login successful, Welcome {row[1]}!"
    return False, "Invalid PIN."


def update_user_details(user_unique_id, First_name=None, Last_name=None, new_password=None, new_pin=None, **kwargs):
    conn = db_connect()
    c = conn.cursor()
    update_count = 0
    if First_name:
        c.execute("UPDATE users SET first_name=%s WHERE user_unique_id=%s", (First_name, user_unique_id))
        update_count += 1
        
    if Last_name:
        c.execute("UPDATE users SET last_name=%s WHERE user_unique_id=%s", (Last_name, user_unique_id))
        update_count += 1
        
    if new_password:
        c.execute("UPDATE users SET user_pass=%s WHERE user_unique_id=%s", (new_password, user_unique_id))
        update_count += 1
        
    if new_pin:
        c.execute("UPDATE users SET pin=%s WHERE user_unique_id=%s", (new_pin, user_unique_id))
        update_count += 1
    
    if update_count > 0:
        conn.commit()
        conn.close()
    else:
        conn.close()
        return "⚠️ No changes made."

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long [alpha-numeric with capital letter/s and special character]."

    if not re.search("[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search("[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search("[0-9]", password):
        return False, "Password must contain at least one number."

    if not re.search("[!@#$%^&*()_\-+=\[\]{};:'\",.<>?/\|`~]", password):
        return False, "Password must contain at least one special character (`~!@#$%^&*`)."
    return True, "Strong password."





# Run only if script executed directly
if __name__ == "__main__":
    create_tables()
    print("Database setup completed Successfully.")