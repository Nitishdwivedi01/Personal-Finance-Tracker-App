# finance_manager_gui_all_in_one.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkcalendar import DateEntry
from datetime import datetime, timedelta, date
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.pdfgen import canvas


from Analysis import (monthly_analysis, yearly_analysis, weekly_analysis,
    analysis_last_n_days, upcoming_bills, )

from Database import(db_connect, register_user, login_user,login_with_pin,
    update_user_details, validate_password, create_tables)

from Expanse import (add_expense, fetch_expenses, delete_expense,get_user_id_name,
    add_multiple_expenses, edit_expense,check_budget_alert,set_budget)
 

# ensure tables exist
create_tables()

# ---------------- Main Window ----------------
root = tk.Tk()
root.title("Personal Finance Manager- Designed & Devloped by 'NITISH'")
root.geometry("1200x720")
root.config(bg="#f4f8f8")

style = ttk.Style()
style.theme_use("clam")

tabs = ttk.Notebook(root)
tab_login = ttk.Frame(tabs)
tab_register = ttk.Frame(tabs)
tab_dashboard = ttk.Frame(tabs)
tab_profile = ttk.Frame(tabs)

tabs.add(tab_login, text="Login")
tabs.add(tab_register, text="Register")
tabs.add(tab_dashboard, text="Dashboard")
tabs.add(tab_profile, text="Profile")
tabs.pack(expand=1, fill="both")



current_user = tk.StringVar()

# ---------------- Login Tab ----------------
ttk.Label(tab_login, text="Unique User Id:", font=("Arial", 11)).pack(pady=(30,6))
login_username_entry = ttk.Entry(tab_login, width=30)
login_username_entry.pack()

ttk.Label(tab_login, text="Password", font=("Arial", 11)).pack(pady=(12,6))
login_pass_entry = ttk.Entry(tab_login, show="*", width=30)
login_pass_entry.pack()

ttk.Label(tab_login, text="OR", font=("Arial", 8)).pack(pady=(12,6))

ttk.Label(tab_login, text="PIN:", font=("Arial", 11)).pack(pady=(12,6))
login_pin_entry = ttk.Entry(tab_login, show="*", width=30)
login_pin_entry.pack()

def do_user_login():
    
    u = login_username_entry.get().strip()
    p = login_pass_entry.get()
    success, msg = login_user(u, p)

    if success:
        current_user.set(u)
        messagebox.showinfo("Login Successful", msg)
        tabs.select(tab_dashboard)
        update_profile_display()
        load_dashboard()
        login_pass_entry.delete(0, tk.END)
        
    else:
        messagebox.showerror("Login Failed", msg)

def do_pin_login():
    
    u = login_username_entry.get().strip()
    p = login_pin_entry.get().strip()
    success, msg = login_with_pin(u, p)
    
    if success:
        current_user.set(u)
        messagebox.showinfo("Login", msg)
        tabs.select(tab_dashboard)
        update_profile_display()
        load_dashboard()
        # login_username_entry.delete(0, tk.END)

    else:
        messagebox.showerror("Login Failed", msg)


ttk.Button(tab_login, text="Login (Password)", command=do_user_login).pack(pady=12)
ttk.Button(tab_login, text="Login (PIN)", command=do_pin_login).pack(pady=8)

# ---------------- Register Tab ----------------
ttk.Label(tab_register, text="First name:", font=("Arial", 11)).pack(pady=(20,6))
reg_first_name_entry = ttk.Entry(tab_register, width=30)
reg_first_name_entry.pack()

ttk.Label(tab_register, text="Last name:", font=("Arial", 11)).pack(pady=(20,6))
reg_last_name_entry = ttk.Entry(tab_register, width=30)
reg_last_name_entry.pack()

ttk.Label(tab_register, text="Create Password:", font=("Arial", 11)).pack(pady=(12,6))
reg_pass_entry = ttk.Entry(tab_register, show="*", width=30)
reg_pass_entry.pack()

def do_register():
    first_name = reg_first_name_entry.get().strip()
    last_name = reg_last_name_entry.get().strip()
    username = str(f"{first_name}{last_name}").strip()

    
    password = reg_pass_entry.get().strip()
    
    if not (first_name and last_name and password):
        messagebox.showerror("Error", "Enter First name, Last name and Password.")
        return
    # Checking password strength
    valid, msg = validate_password(password)
    if not valid:
        messagebox.showerror("Weak Password", msg)
        return 
    # Register user if password is up to mark
    success, msg = register_user(first_name, last_name, password)
    if success:
        messagebox.showinfo("Registered Succesfully", msg)
        reg_first_name_entry.delete(0, tk.END)
        reg_last_name_entry.delete(0, tk.END)
        reg_pass_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", msg)

ttk.Button(tab_register, text="Register", command=do_register).pack(pady=12)

# ---------------- Dashboard Tab ----------------
# Left panel: inputs and controls
left = ttk.Frame(tab_dashboard, width=360)
left.pack(side="left", fill="y", padx=10, pady=10)
# Right panel: table + charts + analysis
right = ttk.Frame(tab_dashboard)
right.pack(side="right", fill="both", expand=1, padx=10, pady=10)

# -- Add Single Expense --
ttk.Label(left, text="Add Expense", font=("Arial", 12, "bold")).pack(anchor="center",pady=6)

ttk.Label(left, text="Category:").pack(anchor="w")
cat_entry = ttk.Entry(left, width=30)
cat_entry.pack(pady=3)

ttk.Label(left, text="Amount:").pack(anchor="w")
amt_entry = ttk.Entry(left, width=30)
amt_entry.pack(pady=3)

ttk.Label(left, text="Date:").pack(anchor="w")
date_entry = DateEntry(left, width=27, date_pattern='yyyy-mm-dd')
date_entry.pack(pady=3)


def add_single_expense_action():

    user_id = current_user.get()
    cat = cat_entry.get().strip()
    try:
        amt = float(amt_entry.get().strip())
    except:
        messagebox.showerror("Error", "Amount must be numeric.")
        return
    dt = date_entry.get_date().strftime("%Y-%m-%d")
    if not cat:
        messagebox.showerror("Error", "Category required.")
        return
    add_expense(user_id, cat, amt, dt)
    messagebox.showinfo("Success", "Expense added Succesfully.")
    cat_entry.delete(0, tk.END)
    amt_entry.delete(0, tk.END)
    load_table()
    update_analysis_charts_and_alerts()

ttk.Button(left, text="Add Expense", command=add_single_expense_action).pack(pady=6)

# -- Add Multiple Expenses (loop)
def add_multiple_popup():
    user_id = current_user.get()
    if not user_id:
        messagebox.showerror("Error", "Please login first.")
        return
    count = simpledialog.askinteger("Multiple Entries", "How many entries to add?", minvalue=1, maxvalue=100)
    if not count:
        return
    entries = []
    for i in range(count):
        cat = simpledialog.askstring("Category", f"Entry {i+1} - Category:")
        if cat is None:
            continue
        amt = simpledialog.askfloat("Amount", f"Entry {i+1} - Amount:")
        if amt is None:
            continue
        dt = simpledialog.askstring("Date", f"Entry {i+1} - Date (YYYY-MM-DD):", initialvalue=date.today().isoformat())
        if not (cat and amt and dt):
            continue
        entries.append({"category": cat, "amount": amt, "date": dt})
    if entries:
        add_multiple_expenses(user_id, entries)
        messagebox.showinfo("Success", f"Added {len(entries)} expenses.")
        load_table()
        update_analysis_charts_and_alerts()

ttk.Button(left, text="Add Multiple Expenses", command=add_multiple_popup).pack(pady=6)

# -- Budget controls
ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)
ttk.Label(left, text="Monthly Budget (YYYY-MM)", font=("Arial", 11, "bold")).pack(pady=4)
budget_month_entry = ttk.Entry(left, width=20)
budget_month_entry.insert(0, datetime.now().strftime("%Y-%m"))
budget_month_entry.pack(pady=3)
budget_amount_entry = ttk.Entry(left, width=20)
budget_amount_entry.pack(pady=3)

def set_budget_action_gui():
    User_unique_id= current_user.get()
    if not User_unique_id:
        messagebox.showerror("Error", "Login first.")
        return
    user = get_user_id_name(User_unique_id)
    if not user:
        messagebox.showerror("Error", "Login first.")
        return
    m = budget_month_entry.get().strip()
    try:
        amt = float(budget_amount_entry.get().strip())
    except:
        messagebox.showerror("Error", "Budget must be numeric.")
        return

    set_budget(user["User_id"], user["username"], m, amt)
    messagebox.showinfo("Success", f"Budget set for {m}.")
    update_analysis_charts_and_alerts()

ttk.Button(left, text="Set Budget", command=set_budget_action_gui).pack(pady=6)

# -- Delete / Edit selected
ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)
ttk.Label(left, text="Edit / Delete", font=("Arial", 11, "bold")).pack(pady=4)

def delete_selected():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a row first.")
        return
    eid = tree.item(sel[0])["values"][0]
    delete_expense(eid)
    load_table()
    update_analysis_charts_and_alerts()
    messagebox.showinfo("Deleted", "Expense removed.")

def edit_selected():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select a row first.")
        return
    row = tree.item(sel[0])["values"]
    eid = row[0]
    new_cat = simpledialog.askstring("Edit", "New Category:", initialvalue=row[1])
    new_amt = simpledialog.askfloat("Edit", "New Amount:", initialvalue=row[2])
    new_date = simpledialog.askstring("Edit", "New Date (YYYY-MM-DD):", initialvalue=row[3])
    edit_expense(eid, new_category=new_cat, new_amount=new_amt, new_date=new_date)
    load_table()
    update_analysis_charts_and_alerts()
    messagebox.showinfo("Edited", "Expense updated.")

ttk.Button(left, text="Edit Selected", command=edit_selected).pack(pady=6)
ttk.Button(left, text="Delete Selected", command=delete_selected).pack(pady=6)

# -- Export Buttons
ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)
ttk.Button(left, text="Export to Excel", command=lambda: export_all_excel()).pack(pady=4)
ttk.Button(left, text="Export to PDF", command=lambda: export_report_pdf()).pack(pady=4)

# -- Exit Button
ttk.Button(root, text="Exit", command=root.destroy).pack(pady=10)


# ---------------- Right panel: Table, Charts, Analysis ----------------
# Table of expenses
table_frame = ttk.Frame(right)
table_frame.pack(fill="both", expand=1, padx=8, pady=8)

cols = ("ID", "Category", "Amount", "Date")
tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, anchor="center")
tree.pack(side="left", fill="both", expand=1)
scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll.set)
scroll.pack(side="right", fill="y")

def load_table():
    for r in tree.get_children():
        tree.delete(r)
    u = current_user.get()
    if not u:
        return
    rows = fetch_expenses(u)
    for r in rows:
        tree.insert("", tk.END, values=r)

# Charts area (embedded figures)
chart_area = ttk.Frame(right)
chart_area.pack(fill="both", expand=1, padx=8, pady=6)

fig_bar, ax_bar = plt.subplots(figsize=(6,2.8))
fig_pie, ax_pie = plt.subplots(figsize=(4,3.5))
canvas_bar = FigureCanvasTkAgg(fig_bar, master=chart_area)
canvas_pie = FigureCanvasTkAgg(fig_pie, master=chart_area)
canvas_bar.get_tk_widget().pack(side="top", fill="x", pady=4)
canvas_pie.get_tk_widget().pack(side="top", pady=4)

# Analysis controls
analysis_frame = ttk.Frame(right)
analysis_frame.pack(fill="x", pady=6)

ttk.Label(analysis_frame, text="Analysis:").pack(side="left", padx=(6,4))
analysis_var = tk.StringVar(value="Monthly")
analysis_menu = ttk.Combobox(analysis_frame, textvariable=analysis_var, values=["Weekly","Monthly","Yearly","Last N Days"], width=15, state="readonly")
analysis_menu.pack(side="left", padx=4)

n_days_entry = ttk.Entry(analysis_frame, width=6)
n_days_entry.pack(side="left", padx=4)
n_days_entry.insert(0, "7")

def run_analysis():
    user_id = current_user.get()
    if not user_id:
        messagebox.showerror("Error", "Login first.")
        return
    mode = analysis_var.get()
    if mode == "Monthly":
        month = simpledialog.askstring("Month", "Enter month (YYYY-MM):", initialvalue=datetime.now().strftime("%Y-%m"))
        if not month:
            return
        total, breakdown = monthly_analysis(user_id, month)
        msg = f"Monthly ({month}) Total: {total}\nCategory breakdown:\n"
        for k,v in breakdown.items():
            msg += f" - {k}: {v}\n"
        messagebox.showinfo("Monthly Analysis", msg)
    elif mode == "Yearly":
        year = simpledialog.askstring("Year", "Enter year (YYYY):", initialvalue=datetime.now().strftime("%Y"))
        if not year:
            return
        df = yearly_analysis(user_id, year)
        if df.empty:
            messagebox.showinfo("Yearly Analysis", "No data for that year.")
            return
        s = "\n".join([f"{row['month']}: {row['total']}" for _, row in df.iterrows()])
        messagebox.showinfo("Yearly Analysis", f"Yearly totals:\n{s}")
    elif mode == "Weekly":
        start = simpledialog.askstring("Start Date", "Enter start date (YYYY-MM-DD):", initialvalue=(date.today() - timedelta(days=7)).isoformat())
        end = simpledialog.askstring("End Date", "Enter end date (YYYY-MM-DD):", initialvalue=date.today().isoformat())
        if not (start and end):
            return
        w = weekly_analysis(user_id, start, end)
        s = "\n".join([f"Week {k}: {v}" for k,v in w.items()])
        messagebox.showinfo("Weekly Analysis", s if s else "No data")
    else:  # Last N Days
        try:
            n = int(n_days_entry.get().strip())
            if not (1 <= n <= 30):
                raise ValueError()
        except:
            messagebox.showerror("Error", "Enter N days between 1 and 30.")
            return
        total, breakdown = analysis_last_n_days(user_id, n)
        msg = f"Last {n} days total: {total}\nBreakdown:\n"
        for k,v in breakdown.items():
            msg += f" - {k}: {v}\n"
        messagebox.showinfo("Last N Days Analysis", msg)

ttk.Button(analysis_frame, text="Run", command=run_analysis).pack(side="left", padx=6)

# I:E ratio, Balance, Bill reminders, Budget alert area
status_frame = ttk.Frame(right)
status_frame.pack(fill="x", pady=4)

ie_label = ttk.Label(status_frame, text="I:E Ratio: -")
ie_label.pack(side="left", padx=8)
balance_label = ttk.Label(status_frame, text="Balance Remaining: -")
balance_label.pack(side="left", padx=8)
reminders_btn = ttk.Button(status_frame, text="Show Bill Reminders", command=lambda: show_bill_reminders(7))
reminders_btn.pack(side="right", padx=8)

# ---------- Analysis & Alerts update function ----------
def update_analysis_charts_and_alerts():
    user_id = current_user.get()
    if not user_id:
        ax_bar.clear(); ax_pie.clear()
        canvas_bar.draw(); canvas_pie.draw()
        ie_label.config(text="I:E Ratio: -"); balance_label.config(text="Balance Remaining: -")
        return

    # load expense DF
    rows = fetch_expenses(user_id)
    df = pd.DataFrame(rows, columns=["ID","Category","Amount","Date"])
    if df.empty:
        ax_bar.clear(); ax_pie.clear()
        ax_bar.text(0.5,0.5,"No data", ha='center')
        ax_pie.text(0.5,0.5,"No data", ha='center')
        canvas_bar.draw(); canvas_pie.draw()
        ie_label.config(text="I:E Ratio: -")
        balance_label.config(text="Balance Remaining: -")
    else:
        # Category pie
        cat_sum = df.groupby("Category")["Amount"].sum()
        ax_pie.clear()
        cat_sum.plot.pie(ax=ax_pie, autopct='%1.1f%%', ylabel='')
        ax_pie.set_title("Spending by Category")
        canvas_pie.draw()

        # Monthly bar chart
        df['Month'] = df['Date'].str.slice(0,7)
        mon = df.groupby("Month")["Amount"].sum().reset_index()
        ax_bar.clear()
        ax_bar.bar(mon['Month'], mon['Amount'])
        ax_bar.set_title("Monthly Spending")
        ax_bar.set_ylabel("Amount")
        ax_bar.tick_params(axis='x', rotation=45)
        canvas_bar.draw()

        # I:E ratio & balance (ask user for income quick)
        # Try to get income from simple dialog once per session — else show '-' if not provided
        income = getattr(update_analysis_charts_and_alerts, "income_value", None)
        if income is None:
            # prompt once silently
            try:
                if messagebox.askyesno("Income Input", "Would you like to enter monthly income now (used for I:E and balance)?"):
                    v = simpledialog.askfloat("Income", "Enter income amount:")
                    if v is not None:
                        update_analysis_charts_and_alerts.income_value = v
                        income = v
            except:
                income = None
        if income is not None:
            total_exp = df['Amount'].sum()
            ratio = income / total_exp if total_exp > 0 else float('inf')
            ie_label.config(text=f"I:E Ratio: {ratio:.2f}" if total_exp>0 else "I:E Ratio: ∞")
            balance_label.config(text=f"Balance Remaining: {income - total_exp:.2f}")
        else:
            ie_label.config(text="I:E Ratio: -")
            balance_label.config(text="Balance Remaining: -")

    # Budget alerts
    # Check current month and category budgets
    month = datetime.now().strftime("%Y-%m")
    alerts = check_budget_alert(user_id, month)
    if alerts:
        msg = "Budget alerts:\n"
        for a in alerts:
            msg += f"{a['category']}: Spent {a['spent']} / Budget {a['budget']}\n"
        # Show non-blocking info (only once per update) - use a small popup
        messagebox.showwarning("Budget Alert", msg)

def show_bill_reminders(days=7):
    u = current_user.get()
    if not u:
        messagebox.showerror("Error", "Login first.")
        return
    df = upcoming_bills(u, days)
    if not df:
        messagebox.showinfo("Bill Reminders", "No upcoming bills.")
        return
    s = ""
    for r in df:
        s += f"{r['date']} - {r['category']} - {r['amount']}\n"
    messagebox.showinfo("Bill Reminders", s)

# ---------------- Profile Tab ----------------

# getting the user data from database which will be used in profile tab and required operations.
def curent_user_data_fetch():
    user_unique_id = current_user.get()
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, last_name, username, user_unique_id, user_pass, pin, created_at FROM users WHERE user_unique_id=%s", (user_unique_id,))
    row = c.fetchone()
    conn.close()

    current_user_data = {
        "user_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "username": row[3],
        "user_unique_id": row[4],
        "user_pass": row[5],
        "pin": row[6],
        "created_at": row[7]
    }
    
    return current_user_data

profile_info_frame = ttk.Frame(tab_profile)
profile_info_frame.pack(pady=10)

us_profile_title = ttk.Label(profile_info_frame, text="User Profile", font=("Arial", 14, "bold"))
us_profile_title.pack(pady=6)

us_uid = ttk.Label(profile_info_frame, text="User ID: -", font=("Arial", 11))
us_uid.pack(anchor="w", padx=10)

us_username = ttk.Label(profile_info_frame, text="Username: -", font=("Arial", 11))
us_username.pack(anchor="w", padx=10)

us_unique_id = ttk.Label(profile_info_frame, text="unique User ID: -", font=("Arial", 11))
us_unique_id.pack(anchor="w", padx=10)

us_created_at = ttk.Label(profile_info_frame, text="Create Date: -", font=("Arial", 11))
us_created_at.pack(anchor="w", padx=10)

def update_profile_display():
    
    current_user_data = curent_user_data_fetch()
    uid = current_user_data.get("user_id")
    un = current_user_data.get("username")
    u = current_user_data.get("user_unique_id")
    ucd = current_user_data.get("created_at")
    
    if not current_user_data:
        us_uid.config(text="User ID: -")
        us_username.config(text="Username: -")
        us_unique_id.config(text="User Unique ID: -")
        us_created_at.config(text="Created At: -")
        return
    
    us_uid.config(text=f"User ID: {uid}")
    us_username.config(text=f"Username: {un}")
    us_unique_id.config(text=f"User Unique ID: {u}")
    us_created_at.config(text=f"Created At: {ucd}")
    
# ---------------- Profile Update Controls ----------------
ttk.Label(tab_profile, text="Change First Name:", font=("Arial", 11)).pack(pady=(20,4))
user_new_fn = ttk.Entry(tab_profile, width=30)
user_new_fn.pack(pady=4)

ttk.Label(tab_profile, text="Change Last Name:", font=("Arial", 11)).pack(pady=(20,4))
user_new_ln = ttk.Entry(tab_profile, width=30)
user_new_ln.pack(pady=4)

ttk.Label(tab_profile, text="Change Password:", font=("Arial", 11)).pack(pady=(20,4))
profile_new_pass = ttk.Entry(tab_profile, show="*", width=30)
profile_new_pass.pack(pady=4)

ttk.Label(tab_profile, text="New PIN (4 digits):", font=("Arial", 11)).pack(pady=(20,4))
profile_new_pin = ttk.Entry(tab_profile, width=30)
profile_new_pin.pack(pady=4)

def do_update_profile():
    current_user_data = curent_user_data_fetch()
    u = current_user_data.get("user_unique_id")
    if not u:
        messagebox.showerror("Error", "Login first to make changes.")
        return

    pw = profile_new_pass.get().strip()
    pin = profile_new_pin.get().strip()
    fn = user_new_fn.get().strip()
    ln = user_new_ln.get().strip()
    
    if not (pin or pw or fn or ln):
        messagebox.showinfo("No Update", "You didn't make any changes.")
        return
         
    if not fn:
        messagebox.showerror("Note", "First name remains unchanged.")
        fn == None
    
    if not ln:
        messagebox.showerror("Note", "Last name remains unchanged.")
        ln == None

    if pw:
        is_valid, msg = validate_password(pw)
        if not is_valid:
            messagebox.showerror("Invalid Password", msg)
            return
        old_password = current_user_data.get("user_pass")
        if pw == old_password:
            messagebox.showerror("Error", "New password cannot be same as old password, please generate new one.")
            return
    
    if pin:
        if not pin.isdigit() or len(pin) != 4:
            messagebox.showerror("Error", "PIN must be 4 digits(numeric).")
            return
    
        if pin == current_user_data.get("pin"):
            messagebox.showerror("Error", "New PIN cannot be same as old PIN, please generate new one.")
            return  


    updated = update_user_details(user_unique_id = u, 
                                  First_name=fn if fn else None,
                                  Last_name=ln if ln else None,
                                  new_password=pw if pw else None, 
                                  new_pin=pin if pin else None)

    # Update saved PIN locally too
    if "updated successfully" in updated:
        messagebox.showinfo("Success", updated)
    else:
        messagebox.showwarning("No Update", updated)
        profile_new_pass.delete(0, tk.END)
        profile_new_pin.delete(0, tk.END)
        user_new_fn.delete(0,tk.END)
        user_new_ln.delete(0, tk.END)
        
ttk.Button(tab_profile, text="Update Profile", command=do_update_profile).pack(pady=8)
ttk.Button(tab_profile, text="Logout", command=lambda: do_logout()).pack(pady=6)

def do_logout():
    current_user.set("")
    # login_user_entry.delete(0, tk.END)
    login_pass_entry.delete(0, tk.END)
    tabs.select(tab_login)
    load_table()
    update_analysis_charts_and_alerts()
    
# def do_update_profile():
#     u = current_user.get()
#     if not u:
#         messagebox.showerror("Error", "Login first.")
#         return
#     pw = profile_new_pass.get().strip()
#     pin = profile_new_pin.get().strip()
#     if pin and (not pin.isdigit() or len(pin) != 4):
#         messagebox.showerror("Error", "PIN must be 4 digits.")
#         return
#     update_user_details(u, new_password=pw if pw else None, new_pin=pin if pin else None)
#     messagebox.showinfo("Success", "Profile updated.")
#     profile_new_pass.delete(0, tk.END)
#     profile_new_pin.delete(0, tk.END)


# ---------------- Export functions ----------------
def export_all_excel():
    u = current_user.get()
    if not u:
        messagebox.showerror("Error", "Login first.")
        return
    rows = fetch_expenses(u)
    if not rows:
        messagebox.showwarning("No Data", "No expenses to export.")
        return
    df = pd.DataFrame(rows, columns=["ID","Category","Amount","Date"])
    file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
    if file:
        df.to_excel(file, index=False)
        messagebox.showinfo("Exported", f"Exported to {file}")

def export_report_pdf():
    u = current_user.get()
    if not u:
        messagebox.showerror("Error", "Login first.")
        return
    rows = fetch_expenses(u)
    if not rows:
        messagebox.showwarning("No Data", "No expenses to export.")
        return
    df = pd.DataFrame(rows, columns=["ID","Category","Amount","Date"])
    file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
    if not file:
        return
    c = canvas.Canvas(file)
    width, height = 595, 842  # A4-ish
    y = height - 40
    c.setFont("Helvetica", 12)
    c.drawString(30, y, f"Expense Report - {u}")
    y -= 20
    c.setFont("Helvetica", 10)
    for idx, row in df.iterrows():
        line = f"{row['Date']} | {row['Category']} | {row['Amount']}"
        c.drawString(30, y, line)
        y -= 14
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)
    c.save()
    messagebox.showinfo("Exported", f"PDF saved to {file}")

# ---------------- Tabs change guard ----------------
def on_tab_change(event):
    tab = event.widget.tab(event.widget.select(), "text")
    if tab in ("Dashboard","Profile"):
        if not current_user.get():
            messagebox.showwarning("Login Required", "Please login first.")
            tabs.select(tab_login)
        else:
            if tab == "Dashboard":
                load_dashboard()
            elif tab == "Profile":
                update_profile_display()
                
tabs.bind("<<NotebookTabChanged>>", on_tab_change)

# ---------------- Load dashboard helpers ----------------
def load_dashboard():
    load_table()
    update_analysis_charts_and_alerts()

# initialize UI
load_table()
update_analysis_charts_and_alerts()

root.mainloop()