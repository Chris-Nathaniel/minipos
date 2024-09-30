import sqlite3

def SQL(database):
    conn = sqlite3.connect(database, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn.cursor()