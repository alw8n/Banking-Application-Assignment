import mysql.connector
import random
import re
from datetime import datetime

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="aaron",  
    database='banking_system'
)
cursor = conn.cursor()

# Function to initialize the database and tables if they don't exist
def initialize_database():
    cursor.execute("CREATE DATABASE IF NOT EXISTS banking_system")
    cursor.execute("USE banking_system")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        account_number VARCHAR(10) UNIQUE NOT NULL,
        dob DATE NOT NULL,
        city VARCHAR(100) NOT NULL,
        password VARCHAR(255) NOT NULL,
        balance DECIMAL(10, 2) NOT NULL,
        contact_number VARCHAR(15) NOT NULL,
        email VARCHAR(255) NOT NULL,
        address TEXT NOT NULL,
        status VARCHAR(10) NOT NULL DEFAULT 'Active'
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaction (
        id INT AUTO_INCREMENT PRIMARY KEY,
        account_number VARCHAR(10) NOT NULL,
        type VARCHAR(10) NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        date DATETIME NOT NULL
    )""")
    
    print("Database and tables initialized.")

initialize_database()

# Validation functions
def validate_email(email):
    return re.match(r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b$', email)

def validate_password(password):
    return len(password) >= 8 and any(char.isdigit() for char in password)

def validate_contact(contact):
    return re.match(r'^\d{10}$', contact)

# Add User
def add_user():
    name = input("Enter Name: ")
    dob = input("Enter DOB (YYYY-MM-DD): ")
    city = input("Enter City: ")
    password = input("Enter Password: ")
    if not validate_password(password):
        print("Password must be at least 8 characters with a number.")
        return
    
    balance = float(input("Enter Initial Balance (min 2000): "))
    if balance < 2000:
        print("Minimum balance must be 2000.")
        return

    contact_number = input("Enter Contact Number: ")
    if not validate_contact(contact_number):
        print("Invalid Contact Number!")
        return
    
    email = input("Enter Email ID: ")
    if not validate_email(email):
        print("Invalid Email ID!")
        return

    address = input("Enter Address: ")
    account_number = str(random.randint(1000000000, 9999999999))

    cursor.execute('''
    INSERT INTO users (name, account_number, dob, city, password, balance, contact_number, email, address)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (name, account_number, dob, city, password, balance, contact_number, email, address))
    conn.commit()
    print(f"User added successfully! Account Number: {account_number}")

# Show User
def show_user():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    if not users:
        print("No users found.")
        return

    for user in users:
        print(f"""
        Name: {user[1]}
        Account Number: {user[2]}
        DOB: {user[3]}
        City: {user[4]}
        Balance: {user[6]}
        Contact: {user[7]}
        Email: {user[8]}
        Address: {user[9]}
        """)

# Transfer Amount
def transfer_amount(logged_in_user):
    from_acc = logged_in_user  
    to_acc = input("Enter Beneficiary Account Number: ")
    amount = float(input("Enter Amount to Transfer: "))
    
    cursor.execute("SELECT balance FROM users WHERE account_number=%s AND status='Active'", (from_acc,))
    sender_balance = cursor.fetchone()

    if not sender_balance or sender_balance[0] < amount:
        print("Insufficient balance or inactive account.")
        return

    cursor.execute("SELECT * FROM users WHERE account_number=%s AND status='Active'", (to_acc,))
    if not cursor.fetchone():
        print("Beneficiary account not found or inactive.")
        return

    cursor.execute("UPDATE users SET balance=balance-%s WHERE account_number=%s", (amount, from_acc))
    cursor.execute("UPDATE users SET balance=balance+%s WHERE account_number=%s", (amount, to_acc))
    
    cursor.execute("INSERT INTO transaction (account_number, type, amount, date) VALUES (%s, 'Debit', %s, %s)",
                   (from_acc, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    cursor.execute("INSERT INTO transaction (account_number, type, amount, date) VALUES (%s, 'Credit', %s, %s)",
                   (to_acc, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    print("Transfer successful.")

# Activate/Deactivate Account
def change_account_status(logged_in_user):
    if logged_in_user: 
        acc_number = logged_in_user
        new_status = input("Enter New Status (Active/Inactive): ")
        cursor.execute("UPDATE users SET status=%s WHERE account_number=%s", (new_status, acc_number))
        conn.commit()
        print("Account status updated.")
    else:
        print("Action not allowed. Please log in first.")

# Change Password
def change_password(logged_in_user):
    if logged_in_user: 
        acc_number = logged_in_user
        old_password = input("Enter Old Password: ")
        new_password = input("Enter New Password: ")
        cursor.execute("SELECT * FROM users WHERE account_number=%s AND password=%s", (acc_number, old_password))
        if not cursor.fetchone():
            print("Incorrect old password.")
            return

        cursor.execute("UPDATE users SET password=%s WHERE account_number=%s", (new_password, acc_number))
        conn.commit()
        print("Password changed successfully.")
    else:
        print("Action not allowed. Please log in first.")

# Update Profile
def update_profile(logged_in_user):
    if logged_in_user: 
        acc_number = logged_in_user
        new_email = input("Enter New Email: ")
        new_contact = input("Enter New Contact Number: ")
        new_address = input("Enter New Address: ")
        cursor.execute('''
        UPDATE users SET email=%s, contact_number=%s, address=%s WHERE account_number=%s
        ''', (new_email, new_contact, new_address, acc_number))
        conn.commit()
        print("Profile updated successfully.")
    else:
        print("Action not allowed. Please log in first.")


# Login
def login():
    acc_number = input("Enter Account Number: ")
    password = input("Enter Password: ")

    cursor.execute("SELECT * FROM users WHERE account_number=%s AND password=%s", (acc_number, password))
    user = cursor.fetchone()

    if not user:
        print("Invalid login credentials.")
        return None

    print(f"Welcome, {user[1]}!")
    return user[2]  

# Main Menu
logged_in_user = None  
while True:
    print("""
    BANKING SYSTEM
    1. Add User
    2. Show User
    3. Login
    4. Exit
    """)
    choice = input("Enter your choice: ")
    if choice == "1":
        add_user()
    elif choice == "2":
        show_user()
    elif choice == "3":
        logged_in_user = login()
        if logged_in_user:
            while True:
                print("""
                1. Show Balance
                2. Show Transactions
                3. Credit Amount
                4. Debit Amount
                5. Transfer Amount
                6. Activate/Deactivate Account
                7. Change Password
                8. Update Profile
                9. Logout
                """)
                choice = input("Enter your choice: ")

                if choice == "1":  
                    cursor.execute("SELECT balance FROM users WHERE account_number=%s", (logged_in_user,))
                    updated_balance = cursor.fetchone()[0]
                    print(f"Your Balance: {updated_balance:.2f}")
                elif choice == "2":
                    cursor.execute("SELECT * FROM transaction WHERE account_number=%s", (logged_in_user,))
                    transactions = cursor.fetchall()
                    if not transactions:
                        print("No transactions found.")
                    else:
                        for t in transactions:
                            print(f"{t[3]} | {t[2]} | Amount: {t[3]}")
                elif choice == "3":
                    amount = float(input("Enter amount to credit: "))
                    cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number=%s", (amount, logged_in_user,))
                    cursor.execute("INSERT INTO transaction (account_number, type, amount, date) VALUES (%s, 'Credit', %s, %s)",
                    (logged_in_user, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    print("Amount credited.")
                elif choice == "4":  
                    amount = float(input("Enter amount to debit: "))
                    cursor.execute("SELECT balance FROM users WHERE account_number=%s", (logged_in_user,))
                    current_balance = cursor.fetchone()[0]
                    
                    if current_balance < amount:
                        print("Insufficient balance.")
                    else:
                        cursor.execute("UPDATE users SET balance = balance - %s WHERE account_number=%s", (amount, logged_in_user,))
                        cursor.execute("""
                        INSERT INTO transaction (account_number, type, amount, date) 
                        VALUES (%s, 'Debit', %s, %s)
                        """, (logged_in_user, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        print("Amount debited.")

                elif choice == "5":
                    transfer_amount(logged_in_user)
                elif choice == "6":
                    change_account_status(logged_in_user)
                elif choice == "7":
                    change_password(logged_in_user)
                elif choice == "8":
                    update_profile(logged_in_user)
                elif choice == "9":
                    print("Logged out.")
                    logged_in_user = None
                    break
                else:
                    print("Invalid choice!")
    elif choice == "4":
        print("Thank you for using the Banking System!")
        break
    else:
        print("Invalid choice! Try again.")
