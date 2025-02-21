from flask import redirect, render_template, request, session
import requests
from functools import wraps
import string
from conn import SQL
from dotenv import load_dotenv
import re
import time
import random
import os
import urllib
from datetime import date


load_dotenv()

database_url = os.getenv('DATABASE_URL')
db = SQL(database_url)

def apology(message, categories="", code=400):
    """Render message as an apology to user and include the cart."""
    # Get the cart from the session
    cart = session.get('cart', [])
    total = session.get('total', 0)
    category = session.get('category', [])
    categories = session.get('categories', [])
    if categories:
        return render_template("apology.html", error=code, message=message, cart=cart, total=total, category=category, categories=categories), code
    if not categories:
        return render_template("apologyg.html", error=code, message=message, cart=cart, total=total, category=category, categories=categories), code

def thankYou(message, orderNumber, code=200):
    """Render message as a thank you to user and include the cart."""
    return render_template("thankyou.html", message=message, orderNumber=orderNumber), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function

def parseInt(placeholder):
    cleanValue = int(re.sub(r'[a-zA-Z,|]', '', str(placeholder)).strip())
    return cleanValue

def formatCurrency(currency, value):
    return "{} {:,.0f}".format(currency, value)


def bankTransfer(order_number, total_amount):
    total_amount = parseInt(total_amount)
    request_body = {
        "payment_type" : "bank_transfer",
        "transaction_details" : {
            "order_id" : order_number,
            "gross_amount" : total_amount
        },
        "bank_transfer":{"bank":"bca"},
    }
    return request_body


def generate_random_string(length=5):
    """Generate a random string of fixed length."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

def generate_order_id():
    # Generate a random string
    random_string = generate_random_string()
    
    # Get the current time as a formatted string (YearMonthDayHourMinSec)
    current_time = time.strftime("%Y%m%d%H%M%S")
    
    # Combine the random string and the current time to create an order ID
    order_id = f"{random_string}{current_time}"
    
    return order_id

def generate_order_number(prefix):
    
    # Get the latest order_number
    latest_order_number = db.execute("""
        SELECT order_number
        FROM orders
        WHERE CAST(SUBSTR(order_number, 9) AS INTEGER) = (
            SELECT MAX(CAST(SUBSTR(order_number, 9) AS INTEGER)) FROM orders
        )
    """).fetchone()
    # Generate new order_number with prefix
    if latest_order_number:
        latest_number = int(latest_order_number[0].replace(prefix, '')) + 1
    else:
        latest_number = 1  # Start from 1 if no orders exist yet

    new_order_number = f"{prefix}{latest_number}"
    return new_order_number

def formatOrderNumber(orderNumber):
    result = f"{orderNumber}{date.today()}"
    return result


def clear_session():
    keys_to_keep = ['user_id']  # List of keys you want to keep
    keys_to_delete = [key for key in session.keys() if key not in keys_to_keep]
    
    for key in keys_to_delete:
        session.pop(key, None)

def createImageUrl(image_url, text, text_size=85, text_color="white", x_align="center", y_align="middle"):
    # Base URL for the API
    base_url = "https://textoverimage.moesif.com/image"
    s_image_url = urllib.parse.quote(image_url, safe='')
    s_custom_text = urllib.parse.quote(text, safe='')


    url = f'https://textoverimage.moesif.com/image?image_url={s_image_url}&text={s_custom_text}&text_size={text_size}&y_align=middle&x_align=center'
    return url

def mask_key(key, visible=5):
    """Mask all but the first and last `visible` characters of the key."""
    if len(key) <= visible * 2:
        return key  
    return f"{key[:visible]}{'*' * (len(key) - (visible * 2))}{key[-visible:]}"

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

def sanitize_strings(filename):
    # Remove or replace special characters with underscores
    sanitized = re.sub(r'[^a-zA-Z]', '', filename).strip()
    return sanitized

def generate_name():
    while True:  
        random_letter = random.choice("abcdefghijklmnopqrstuvwxyz")

        # Fetch character data from Jikan v4 API
        response = requests.get(f"https://api.jikan.moe/v4/anime?q={random_letter}&limit=12")
        data = response.json()

        # Check if results are found
        if "data" in data and data["data"]:
            random_character = random.choice(data["data"])['title']
            random_character = sanitize_strings(random_character)

            # If name is at least 5 letters long, return it
            if len(random_character) <= 15 and len(random_character) >= 4:
                return random_character
            
    