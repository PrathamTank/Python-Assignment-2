import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import re

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="contact_manager"
    )

def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS contact_manager")
    cur.close()
    conn.close()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Contact (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            category VARCHAR(50) NOT NULL,
            notes TEXT,
            INDEX idx_name (name),
            INDEX idx_phone (phone)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

def validate_email(email):
    pattern = r"^[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(com|edu|org)$"
    return re.fullmatch(pattern, email, re.IGNORECASE) is not None

def clear_fields():
    id_var.set("")
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    category_var.set("Personal")
    notes_text.delete("1.0", tk.END)

def get_form_data():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    category = category_var.get()
    notes = notes_text.get("1.0", tk.END).strip()

    if not name or not email or not phone:
        messagebox.showerror("Validation Error", "Name, email and phone are required.")
        return None

    if not validate_email(email):
        messagebox.showerror(
            "Validation Error",
            "Enter a valid email ending in .com, .edu or .org."
        )
        return None

    if not re.fullmatch(r"[0-9+\-\s()]{7,20}", phone):
        messagebox.showerror("Validation Error", "Enter a valid phone number.")
        return None

    return name, email, phone, category, notes

def add_contact():
    values = get_form_data()
    if values is None:
        return

    conn = None
    cur = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Contact (name, email, phone, category, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, values)

        conn.commit()
        messagebox.showinfo("Success", "Contact inserted successfully.")
        clear_fields()
        load_contacts()

    except Error as e:
        if e.errno == 1062:
            messagebox.showerror("Duplicate Email", "This email already exists.")
        else:
            messagebox.showerror("Database Error", str(e))

    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def update_contact():
    contact_id = id_var.get()

    if not contact_id:
        messagebox.showerror("Error", "Select a contact to update.")
        return

    values = get_form_data()
    if values is None:
        return

    conn = None
    cur = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Contact
            SET name=%s, email=%s, phone=%s, category=%s, notes=%s
            WHERE id=%s
        """, values + (contact_id,))

        conn.commit()
        messagebox.showinfo("Success", "Contact updated successfully.")
        clear_fields()
        load_contacts()

    except Error as e:
        if e.errno == 1062:
            messagebox.showerror("Duplicate Email", "This email already exists.")
        else:
            messagebox.showerror("Database Error", str(e))

    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def delete_contact():
    contact_id = id_var.get()

    if not contact_id:
        messagebox.showerror("Error", "Select a contact to delete.")
        return

    if not messagebox.askyesno("Confirm", "Delete selected contact?"):
        return

    conn = None
    cur = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("DELETE FROM Contact WHERE id=%s", (contact_id,))
        conn.commit()

        messagebox.showinfo("Success", "Contact deleted successfully.")
        clear_fields()
        load_contacts()

    except Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def search_contacts():
    keyword = search_entry.get().strip()

    for item in contact_table.get_children():
        contact_table.delete(item)

    conn = None
    cur = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, email, phone, category, notes
            FROM Contact
            WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
            ORDER BY name ASC, id ASC
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

        for row in cur:
            contact_table.insert("", tk.END, values=row)

    except Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def load_contacts():
    for item in contact_table.get_children():
        contact_table.delete(item)

    conn = None
    cur = None

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, email, phone, category, notes
            FROM Contact
            ORDER BY name ASC, id ASC
        """)

        for row in cur:
            contact_table.insert("", tk.END, values=row)

    except Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def select_contact(event):
    selected = contact_table.selection()

    if not selected:
        return

    values = contact_table.item(selected[0], "values")

    clear_fields()
    id_var.set(values[0])
    name_entry.insert(0, values[1])
    email_entry.insert(0, values[2])
    phone_entry.insert(0, values[3])
    category_var.set(values[4])
    notes_text.insert("1.0", values[5] or "")

try:
    setup_database()
except Error as e:
    messagebox.showerror("Database Error", str(e))
    raise SystemExit

root = tk.Tk()
root.title("Tkinter Contact Manager")
root.geometry("1150x700")
root.minsize(950, 600)

id_var = tk.StringVar()
category_var = tk.StringVar(value="Personal")

tk.Label(
    root,
    text="Contact Manager",
    font=("Arial", 20, "bold")
).pack(pady=10)

form = tk.Frame(root)
form.pack(pady=5)

tk.Label(form, text="Contact ID").grid(row=0, column=0, padx=5, pady=5)
tk.Entry(form, textvariable=id_var, width=22, state="readonly").grid(row=0, column=1, padx=5)

tk.Label(form, text="Name").grid(row=0, column=2, padx=5)
name_entry = tk.Entry(form, width=25)
name_entry.grid(row=0, column=3, padx=5)

tk.Label(form, text="Email").grid(row=1, column=0, padx=5, pady=5)
email_entry = tk.Entry(form, width=25)
email_entry.grid(row=1, column=1, padx=5)

tk.Label(form, text="Phone").grid(row=1, column=2, padx=5)
phone_entry = tk.Entry(form, width=25)
phone_entry.grid(row=1, column=3, padx=5)

tk.Label(form, text="Category").grid(row=2, column=0, padx=5, pady=5)

category_combo = ttk.Combobox(
    form,
    textvariable=category_var,
    values=["Personal", "Faculty", "Student", "Work", "Other"],
    state="readonly",
    width=22
)
category_combo.grid(row=2, column=1, padx=5)

tk.Label(form, text="Notes").grid(row=2, column=2, padx=5)
notes_text = tk.Text(form, width=25, height=3)
notes_text.grid(row=2, column=3, padx=5)

buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(buttons, text="Add Contact", width=14, command=add_contact).pack(side=tk.LEFT, padx=5)
tk.Button(buttons, text="Update Contact", width=14, command=update_contact).pack(side=tk.LEFT, padx=5)
tk.Button(buttons, text="Delete Contact", width=14, command=delete_contact).pack(side=tk.LEFT, padx=5)
tk.Button(buttons, text="Clear Fields", width=14, command=clear_fields).pack(side=tk.LEFT, padx=5)

search_frame = tk.Frame(root)
search_frame.pack(pady=5)

tk.Label(search_frame, text="Search name/email/phone:").pack(side=tk.LEFT, padx=5)

search_entry = tk.Entry(search_frame, width=35)
search_entry.pack(side=tk.LEFT, padx=5)

tk.Button(search_frame, text="Search", command=search_contacts).pack(side=tk.LEFT, padx=5)
tk.Button(search_frame, text="Show All", command=load_contacts).pack(side=tk.LEFT, padx=5)

table_frame = tk.Frame(root)
table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

columns = ("ID", "Name", "Email", "Phone", "Category", "Notes")

contact_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    contact_table.heading(column, text=column)
    contact_table.column(column, width=150)

contact_table.column("ID", width=55)
contact_table.column("Notes", width=230)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.VERTICAL,
    command=contact_table.yview
)

contact_table.configure(yscrollcommand=scrollbar.set)
contact_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

contact_table.bind("<<TreeviewSelect>>", select_contact)

load_contacts()
root.mainloop()