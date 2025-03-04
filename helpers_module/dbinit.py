import sqlite3
import os
from dotenv import load_dotenv
import logging
import secrets

# Configure logging
logging.basicConfig(
    filename="app.log",  
    level=logging.INFO,  
    format="%(asctime)s [%(levelname)s]: %(message)s",  
)    

def create_database(name="database"):
    db_name = f"{name}.db"
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT NOT NULL,
            hash TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS orderitems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL GENERATED ALWAYS AS (quantity * price) STORED,
            order_time DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_number) REFERENCES orders (order_number) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES menu_list (id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_number TEXT PRIMARY KEY,
            table_number INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK(status IN ('new', 'pending', 'completed', 'cancelled')),
            total_amount REAL,
            type TEXT CHECK(type IN ('dine in', 'take out')) DEFAULT 'dine in',
            discount REAL DEFAULT 0.0
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS payments (
            invoice_number INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            payment_method TEXT CHECK(payment_method IN ('Cash', 'Card', 'BCA Qris', 'm-banking')),
            payment_status TEXT CHECK(payment_status IN ('paid', 'pending', 'unpaid', 'failed')) DEFAULT 'unpaid',
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invoice_amount REAL NOT NULL,
            payment_amount REAL NOT NULL,
            change REAL GENERATED ALWAYS AS (payment_amount - invoice_amount) STORED,
            FOREIGN KEY (order_number) REFERENCES orders(order_number) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS menu_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            image_url TEXT,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL DEFAULT 'Uncategorized',
            date_added DATE DEFAULT CURRENT_DATE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS discount_ticket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            discount INTEGER NOT NULL,
            expiration_date DATE NOT NULL,
            discount_code TEXT UNIQUE,
            image TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS business (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            contact TEXT,
            email TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS password_reset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expiration DATETIME NOT NULL,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (business_id) REFERENCES business(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE virtual_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            va_number TEXT NOT NULL,
            bank_name TEXT NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            expiration DATETIME DEFAULT (DATETIME('now', '+1 hour')),
            count INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_number) REFERENCES orders(id) ON DELETE CASCADE
        );
        """
    ]

    # Create database and tables
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    for table in tables:
        cursor.execute(table)

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully with all tables.")
    return db_name

# Update .env file
def update_env(db_name):
    env_file = ".env"
    app_pass = "desp snde octd wudy"
    token = secrets.token_urlsafe(5)

    # Ensure the .env file exists
    if not os.path.exists(env_file):
        open(env_file, "w").close()  # Create an empty .env file if it doesn't exist

    # Load existing environment variables
    load_dotenv(env_file)

    # Retrieve the old DATABASE_URL if it exists
    old_db_url = os.getenv("DATABASE_URL", "")

    # Use set_key() to update the .env file
    set_key(env_file, "secret", token)
    set_key(env_file, "OLD_DB_URL", old_db_url)
    set_key(env_file, "DATABASE_URL", db_name)
    set_key(env_file, "APP_PASS", app_pass)

    print(".env file updated successfully.")

def set_key(dotenv_path, key, value):
    """Update or add a key-value pair in the .env file without quotes."""
    lines = []
    if os.path.exists(dotenv_path):
        with open(dotenv_path, 'r') as f:
            lines = f.readlines()

    # Remove any existing key
    lines = [line for line in lines if not line.startswith(f"{key}=")]

    # Add new key-value pair
    lines.append(f"{key}={value}\n")

    with open(dotenv_path, 'w') as f:
        f.writelines(lines)