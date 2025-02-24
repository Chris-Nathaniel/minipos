from __init__ import *

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
    env_data = {}
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                key, _, value = line.partition("=")
                env_data[key.strip()] = value.strip()

        env_data["OLD_DB_URL"] = env_data["DATABASE_URL"]  
        
    else:
        env_data["OLD_DB_URL"] = ""

    env_data["DATABASE_URL"] = db_name
    env_data["APP_PASS"] = app_pass

    with open(env_file, "w") as f:
        for key, value in env_data.items():
            f.write(f"{key}={value}\n")

    print(".env file updated successfully.")