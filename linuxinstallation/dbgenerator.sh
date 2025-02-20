#!/bin/bash

set -e  # Exit on error

DB_NAME="$1.db"
ENV_FILE=".env"
TEMP_FILE=".env.tmp"
FOUND_OLD=0
FOUND_DB=0

echo "Creating SQLite database: $DB_NAME"

# Create SQLite database and insert tables
sqlite3 "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);

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
    FOREIGN KEY (item_id) REFERENCES menu_list_old (id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_number TEXT PRIMARY KEY,
    table_number INTEGER,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('new', 'pending', 'completed', 'cancelled')),
    total_amount REAL,
    type TEXT CHECK(type IN ('dine in', 'take out')) DEFAULT 'dine in',
    discount REAL DEFAULT 0.0
);

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

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS menu_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    image_url TEXT,
    description TEXT,
    price REAL NOT NULL,
    category TEXT NOT NULL DEFAULT 'Uncategorized',
    date_added DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS discount_ticket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    discount INTEGER NOT NULL,
    expiration_date DATE NOT NULL,
    discount_code TEXT UNIQUE,
    image TEXT
);

CREATE TABLE IF NOT EXISTS business (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    contact TEXT,
    email TEXT
);
EOF

echo "Database $DB_NAME created successfully!"
echo "All tables created successfully."

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo ".env file not found."
    exit 1
fi

# Read DATABASE_URL from the .env file
OLD_DB_NAME=$(grep -i "^DATABASE_URL=" "$ENV_FILE" | cut -d '=' -f2)

# Process the .env file to update or insert OLD_DB_URL and DATABASE_URL
{
    while IFS='=' read -r key value; do
        if [ "$key" == "OLD_DB_URL" ]; then
            echo "OLD_DB_URL=$OLD_DB_NAME"
            FOUND_OLD=1
        elif [ "$key" == "DATABASE_URL" ]; then
            echo "DATABASE_URL=$DB_NAME"
            FOUND_DB=1
        else
            echo "$key=$value"
        fi
    done < "$ENV_FILE"

    # If OLD_DB_URL was not found, append it
    [ "$FOUND_OLD" -eq 0 ] && echo "OLD_DB_URL=$OLD_DB_NAME"

    # If DATABASE_URL was not found, append it
    [ "$FOUND_DB" -eq 0 ] && echo "DATABASE_URL=$DB_NAME"
} > "$TEMP_FILE"

# Replace the original .env file with the updated one
mv "$TEMP_FILE" "$ENV_FILE"

echo "DATABASE_URL updated successfully to $DB_NAME."
