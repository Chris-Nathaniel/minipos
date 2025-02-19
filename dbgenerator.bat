@echo off
set DB_NAME=mini.db
set ENV_FILE=.env

:: Create SQLite database and insert the tables
echo Creating SQLite database: %DB_NAME%

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);"

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS orderitems (id INTEGER PRIMARY KEY AUTOINCREMENT, order_number TEXT NOT NULL, item_id INTEGER NOT NULL, quantity INTEGER NOT NULL, price REAL NOT NULL, total REAL GENERATED ALWAYS AS (quantity * price) STORED, order_time DATETIME NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (order_number) REFERENCES orders (order_number) ON DELETE CASCADE, FOREIGN KEY (item_id) REFERENCES menu_list_old (id));"

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS orders (order_number TEXT PRIMARY KEY, table_number INTEGER, order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status TEXT CHECK(status IN ('new', 'pending', 'completed', 'cancelled')), total_amount REAL, type TEXT CHECK(type IN ('dine in', 'take out')) DEFAULT 'dine in', discount REAL DEFAULT 0.0);"

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS payments (invoice_number INTEGER PRIMARY KEY AUTOINCREMENT, order_number TEXT NOT NULL, payment_method TEXT CHECK(payment_method IN ('Cash', 'Card', 'BCA Qris', 'm-banking')), payment_status TEXT CHECK(payment_status IN ('paid', 'pending', 'unpaid', 'failed')) DEFAULT 'unpaid', payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, invoice_amount REAL NOT NULL, payment_amount REAL NOT NULL, change REAL GENERATED ALWAYS AS (payment_amount - invoice_amount) STORED, FOREIGN KEY (order_number) REFERENCES orders(order_number) ON DELETE CASCADE);"

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL UNIQUE);"

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS menu_list (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT NOT NULL, image_url TEXT, description TEXT, price REAL NOT NULL, category TEXT NOT NULL DEFAULT 'Uncategorized', date_added DATE DEFAULT CURRENT_DATE);"

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS discount_ticket (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT, discount INTEGER NOT NULL, expiration_date DATE NOT NULL, discount_code TEXT UNIQUE, image TEXT);"

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS business (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, address TEXT, contact TEXT, email TEXT);"

echo Database %DB_NAME% created successfully!
echo All tables created successfully.

:: Check if .env file exists
if exist %ENV_FILE% (
    echo Checking for existing DATABASE_URL in %ENV_FILE%
    
    :: Check if DATABASE_URL exists in the file
    findstr /R "^DATABASE_URL *= *" %ENV_FILE% >nul
    if %errorlevel% == 0 (
        echo Updating DATABASE_URL in %ENV_FILE%
        (for /f "delims=" %%i in ('type %ENV_FILE% ^| findstr /V /R "^DATABASE_URL *= *"') do echo %%i) > temp_env
        echo DATABASE_URL = %DB_NAME% >> temp_env
        move /Y temp_env %ENV_FILE% >nul
    ) else (
        echo Appending DATABASE_URL to %ENV_FILE%
        echo DATABASE_URL = %DB_NAME% >> %ENV_FILE%
    )
) else (
    echo Creating new .env file with DATABASE_URL
    echo DATABASE_URL = %DB_NAME% > %ENV_FILE%
)

echo .env file updated successfully!

exit

