import sqlite3
import os
import secrets
from dotenv import load_dotenv
import midtransclient

def SQL(database):
    conn = sqlite3.connect(database, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn.cursor()

def init_app(app):
    # Load environment variables
    load_dotenv()

    # Set the secret key for the app
    app.secret_key = secrets.token_hex(16)

    # Setup database URL and Midtrans client keys
    database_url = os.getenv('DATABASE_URL')
    server_key = os.getenv('SERVER_KEY')
    client_key = os.getenv('PUBLIC_CLIENT')

    # Setup the Midtrans Core API
    core = midtransclient.CoreApi(
        is_production=False,
        server_key=server_key,
        client_key=client_key
    )

    # Return the initialized API client and database URL for later use
    return core, database_url