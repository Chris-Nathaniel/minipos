@echo off
set DB_NAME=%1.db
set ENV_FILE=.env
set TEMP_FILE=.env.tmp
set FOUND_OLD=0
set FOUND_DB=0

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

sqlite3 %DB_NAME% "CREATE TABLE IF NOT EXISTS password_reset (id INTEGER PRIMARY KEY AUTOINCREMENT, business_id INTEGER NOT NULL, token TEXT UNIQUE NOT NULL, expiration DATETIME NOT NULL, used BOOLEAN DEFAULT 0, FOREIGN KEY (business_id) REFERENCES business(id) ON DELETE CASCADE);"

echo Database %DB_NAME% created successfully!
echo All tables created successfully.

:: Check if .env file exists
if not exist "%ENV_FILE%" (
    type nul > "%ENV_FILE%"
    echo .env file created.
)

:: Read the .env file and search for DATABASE_URL
for /f "tokens=1,* delims==" %%A in (%ENV_FILE%) do (
    if /I "%%A"=="DATABASE_URL" set "OLD_DB_NAME=%%B"
)

:: Process the .env file to update or insert OLD_DB_URL and DATABASE_URL
(for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
    if /I "%%A"=="OLD_DB_URL" (
        echo OLD_DB_URL=%OLD_DB_NAME%
        set FOUND_OLD=1
    ) else if /I "%%A"=="DATABASE_URL" (
        echo DATABASE_URL=%DB_NAME%
        set FOUND_DB=1
    ) else (
        echo %%A=%%B
    )
)) > %TEMP_FILE%

:: If OLD_DB_URL was not found, append it
if %FOUND_OLD%==0 (
    echo OLD_DB_URL=%OLD_DB_NAME% >> %TEMP_FILE%
)

:: If DATABASE_URL was not found, append it
if %FOUND_DB%==0 (
    echo DATABASE_URL=%DB_NAME% >> %TEMP_FILE%
)

:: Replace the original .env file with the updated one
move /Y %TEMP_FILE% %ENV_FILE% > nul

echo DATABASE_URL updated successfully to %DB_NAME%.

exit

