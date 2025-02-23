from helpers_module.__init__ import *


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

def connect_ngrok():
    """Start ngrok tunnel and keep it alive."""
    listener = ngrok.forward(5000, domain=os.getenv("NGROK_DOMAIN"), authtoken=os.getenv("NGROK_AUTH"))
    print(f"ngrok tunnel established: {listener.url()}")

    # Keep ngrok running as long as the app is running
    while threading.main_thread().is_alive():
        time.sleep(1)

app = Flask(__name__)

    # Initialize the app with environment variables and Midtrans client
core, database_url = init_app(app)

# connect to database
db = SQL(database_url)