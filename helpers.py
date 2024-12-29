from flask import redirect, render_template, request, session
from functools import wraps
import string
from conn import SQL
from dotenv import load_dotenv
import re
import time
import random
import os
import secrets
import csv
# import pytz
import requests
import urllib
import uuid

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
    return render_template("apology.html", error=code, message=message, cart=cart, total=total, category=category, categories=categories), code

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
    """).fetchone()[0]
    print(latest_order_number)
    # Generate new order_number with prefix
    if latest_order_number:
        latest_number = int(latest_order_number.replace(prefix, '')) + 1
    else:
        latest_number = 1  # Start from 1 if no orders exist yet

    new_order_number = f"{prefix}{latest_number}"
    return new_order_number


def clear_session():
    keys_to_keep = ['user_id']  # List of keys you want to keep
    keys_to_delete = [key for key in session.keys() if key not in keys_to_keep]
    
    for key in keys_to_delete:
        session.pop(key, None)