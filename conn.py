import sqlite3

print(sqlite3.__file__)
def SQL(database):
    conn = sqlite3.connect(database, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn.cursor()