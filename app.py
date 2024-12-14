from flask import Flask, render_template, request, session, redirect, flash, jsonify, current_app, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from conn import SQL
from helpers import apology, login_required, thankYou, parseInt, formatCurrency, bankTransfer, generate_order_number, clear_session
import midtransclient
import secrets
from dotenv import load_dotenv
import os

# db = SQL('/mnt/c/Users/LEGION/.vscode/github/personal/possystem/minicafe.db')
load_dotenv()
app = Flask(__name__)

database_url = os.getenv('DATABASE_URL')
serverkey = os.getenv('SERVER_KEY')
clientkey = os.getenv('PUBLIC_CLIENT')
db = SQL(database_url)
app.secret_key = secrets.token_hex(16)

core = midtransclient.CoreApi(
    is_production=False,
    server_key=serverkey,
    client_key=clientkey
)


@app.route('/')
@login_required
def choose_option():

    if 'dinein' in request.args:
        # Handle the Take Away option
        session['type'] = "dine in"
        return redirect('/menu')
    if 'takeout' in request.args:
        # Handle the Dine In option
        session['type'] = "take out"
        return redirect('/menu')

    return render_template('index.html')


@app.route("/menu")
@login_required
def menu():
    # check if customer have chosen order type
    if 'type' not in session or not session['type']:
        return redirect("/")    
    query = request.args.get('search')
    if query:
        main = db.execute('SELECT * FROM menu_list WHERE item_name LIKE ?',('%' + query + '%',)).fetchall()
    else: 
        main = db.execute('SELECT * FROM menu_list').fetchall()
    
    # fetch menu list
    categories = db.execute('SELECT DISTINCT category FROM categories').fetchall()
    
    # Fetch the username in current session
    username = db.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    username = username['username']

    # Load Sessions
    cart = session.get('cart', [])
    total = parseInt(session.get('total', 0))  # return str in the format (x,xxx)
    tax = parseInt(session.get('tax', 0))  # return str format (x,xxx)
    cashValue = parseInt(session.get('cashPaid', 0))  # return str format (Rp x,xxx)
    tableNumber = session.get('tableNumber', "")
    deliveryType = session.get('type', 'cart').capitalize()
    finish_edit_order = session.get('edit_order', '')
    change = cashValue - total

    # format them add currency
    if total not in ['0', 0]:
        tax = formatCurrency("Rp", tax)
        total = formatCurrency("Rp", total)

    if cashValue not in ['0', 0]:
        cash = formatCurrency("Rp", cashValue)
        change = formatCurrency("Rp", change)
    else:
        change = 0
        cash = cashValue

    return render_template("menu.html", main=main, cart=cart, total=total, tax=tax, cash=cash, cashValue=cashValue, change=change, deliveryType=deliveryType, tableNumber=tableNumber, finish_edit_order=finish_edit_order, categories=categories, mode="menu")


@app.route("/<category>")
@login_required
def menu_by_category(category):

    # list of valid category
    valid_categories = ["Appetizers", "Main Course", "Side Dish", "Drinks", "Breads", "Desserts", "Additionals"]

    # fetch menu list by category
    main = db.execute('SELECT * FROM menu_list WHERE category Like ?', (category,)).fetchall()
    categories = db.execute('SELECT DISTINCT category FROM categories').fetchall()

     # Handle the case where the category doesn't exist
    if category not in valid_categories:
        return apology("oops , category not found", categories)
    
    if not main:
        session['category'] = category
        return apology("but its empty...", categories)

    # Get the cart from the session
    cart = session.get('cart', [])
    total = parseInt(session.get('total', 0))
    tax = parseInt(session.get('tax', 0))
    cashValue = parseInt(session.get('cashPaid', 0))
    tableNumber = session.get('tableNumber', "")
    deliveryType = session.get('type', 'cart').capitalize()
    finish_edit_order = session.get('edit_order', '')
    change = cashValue - total

    # format them add currency
    if total not in ['0', 0]:
        tax = formatCurrency("Rp", tax)
        total = formatCurrency("Rp", total)

    if cashValue not in ['0', 0]:
        cash = formatCurrency("Rp", cashValue)
        change = formatCurrency("Rp", change)
    else:
        change = 0
        cash = cashValue

    return render_template("menu.html", main=main, cart=cart, total=total, tax=tax, cash=cash, cashValue=cashValue, change=change, deliveryType=deliveryType, category=category, tableNumber=tableNumber, finish_edit_order=finish_edit_order, categories=categories, mode="menu")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 402)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 402)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 402)

         # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # check all fields
        if not username:
            return apology("Username is required!")
        if not password:
            return apology("Passwordis required!")
        if password == confirmation:
            hashed_password = generate_password_hash(password)
        else:
            return apology("please confirm password")

        # check if user already registered, if not registered
        existinguser = db.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchall()
        if existinguser:
            return apology("user already registered", 400)
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?,?)", (username, hashed_password,))
            db.connection.commit()
            return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Route to add items to the cart


@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    
    if 'cart' not in session:
        session['cart'] = []
    gtotal = 0
    itemCount = 0
    # retrieving data
    data = request.json
    item_in_cart = any(item['item_id'] == data['item_id'] for item in session['cart'])
    if item_in_cart:
        # increase the quantity + 1
        for item in session['cart']:
            if item['item_id'] == data['item_id']:
                # Increment the quantity by 1
                item['item_quantity'] = str(int(item['item_quantity']) + 1)
    else:
        # append data to session
        session['cart'].append(data)
        session['cart'] = session['cart']

    for i in session['cart']:
        total = int(i['item_price'].replace(',', '')) * int(i['item_quantity'])
        item_quantity = int(i['item_quantity'])
        # storing the individual total in the cart as dict
        i['total'] = total
        i['total'] = '{:,.0f}'.format(i['total'])
        # storing the global total in session
        gtotal += total
        itemCount += item_quantity

    session['tax'] = '{:,.0f}'.format(gtotal * 0.10)
    session['total'] = '{:,.0f}'.format(gtotal + gtotal * 0.10)
    session['itemCount'] = itemCount
    cash = session.get('cashPaid', 0)

    return jsonify({'cart': session['cart'], 'total': session['total'], 'tax': session['tax'], 'cashPaid': cash, 'itemCount' : session['itemCount']}), 200


@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():

    data = request.json
    if data['ordertime'] == 'undefined':
        del data['ordertime']
    session['cart'] = [item for item in session['cart'] if str(item.get('item_id')) != data.get(
        'item_id') or item.get('order_time') != data.get('ordertime')]
    itemCount = 0
    gtotal = 0
    for i in session['cart']:
        total = int(i['item_price'].replace(',', '')) * int(i['item_quantity'])
        item_quantity = int(i['item_quantity'])
        # storing the individual total in the cart as dict
        i['total'] = total
        i['total'] = '{:,.0f}'.format(i['total'])
        # storing the global total in session
        gtotal += total
        itemCount += item_quantity

    session['tax'] = '{:,.0f}'.format(gtotal * 0.10)
    session['total'] = '{:,.0f}'.format(gtotal)
    session['itemCount'] = itemCount
    cash = session.get('cashPaid', 0)


    return jsonify({'cart': session['cart'], 'total': session['total'], 'tax': session['tax'], 'cashPaid': cash, 'itemCount' : session['itemCount']}), 200


@app.route('/process_order', methods=['POST', 'GET'])
@login_required
def confirm_order():

    orders = session.get("cart", [])
    total_amount = session.get("total", 0)  # the amount customer has to pay
    ordertype = session.get("type", " ")
    payment_method = request.form.get('paymentMethod')
    table = request.form.get('table')
    totalValue = parseInt(total_amount)
    amount = request.form.get('cashValue')
    order_number = generate_order_number("TESTORD-")
    print(order_number)

    if int(amount) < totalValue and payment_method == "Cash":
        flash("Invalid paid amount!", "error")
        return redirect('/menu')

    # check if orders is empty
    if not orders:
        return redirect("/")
    if not table:
        table = 0

    # save order to database
    result = db.execute("INSERT INTO orders (order_number, type, table_number, status, total_amount) VALUES (?, ?, ?, ?, ?) RETURNING order_number, order_date",
                        (order_number, ordertype, table, "new", int(total_amount.replace(",", "")),)).fetchone()

    # Fetch the returned order number and order_date
    order_number, order_date = result
    db.connection.commit()

    # save order items to database
    for order in orders:
        db.execute("INSERT INTO orderitems (order_number, item_id, quantity, price, order_time) VALUES (?, ?, ?, ?, ?)",
                   (order_number, order['item_id'], order['item_quantity'], int(order['item_price'].replace(",", "")), order_date))
        db.connection.commit()

    # check if payment is cash
    if payment_method == "Cash":
       # save payments to database and generate invoice
        db.execute("INSERT INTO payments (order_number, payment_method, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?, ?)",
                   (order_number, payment_method, "paid", totalValue, amount))
        db.connection.commit()
        clear_session()
        return thankYou("Your order has been successfully placed, we hope you enjoy your meal!", order_number)
    # check if payment is card
    if payment_method == "Card":
        db.execute("INSERT INTO payments (order_number, payment_method, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?, ?)",
                   (order_number, payment_method, "paid", totalValue, totalValue))
        db.connection.commit()
        clear_session()
        return thankYou("Your order has been successfully placed, we hope you enjoy your meal!", order_number)
    # check if payment is Bca Qris
    if payment_method == "BCA Qris":
        db.execute("INSERT INTO payments (order_number, payment_method, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?, ?)",
                   (order_number, payment_method, "paid", totalValue, totalValue))
        db.connection.commit()
        clear_session()
        return thankYou("Your order has been successfully placed, we hope you enjoy your meal!", order_number)
    # check if payment is m-banking
    if payment_method == "m-banking":
        param = bankTransfer(order_number, total_amount)
        charge_response = core.charge(param)
        print(charge_response)
        va_number = charge_response['va_numbers'][0]['va_number']
        bank_name = charge_response['va_numbers'][0]['bank']
        db.execute("INSERT INTO payments (order_number, payment_method, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?, ?)",
                   (order_number, payment_method, "pending", totalValue, totalValue))
        db.connection.commit()
        clear_session()
        session['va_number'] = va_number
        session['bank_name'] = bank_name
        session['order_number'] = order_number
        session['total_amount'] = total_amount

        return redirect("/waiting_for_payment")
    if not payment_method:
        db.execute("INSERT INTO payments (order_number, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?)",
                   (order_number, "unpaid", totalValue, 0,))
        db.connection.commit()
        clear_session()
        return thankYou("Your order has been successfully placed, we hope you enjoy your meal!", order_number)


@app.route("/waiting_for_payment", methods=['GET'])
def waiting_for_payment():

    va_number = session.get("va_number", 0)
    bank_name = session.get("bank_name", 0)
    order_number = session.get("order_number", 0)
    total_amount = session.get("total_amount", 0)

    return render_template('payment_process.html', va_number=va_number, bank_name=bank_name, order_number=order_number, total_amount=total_amount)


@app.route('/midtrans/notification', methods=['POST'])
def midtrans_notification():
    # Get the JSON notification from Midtrans
    notification_json = request.get_json()

    # Use Midtrans library to parse and verify the notification
    notification = core.transactions.notification(notification_json)

    # Extract necessary data from the notification
    order_id = notification['order_id']
    transaction_status = notification['transaction_status']

    # If the transaction is successful
    if transaction_status == 'settlement':
        # Update the payment status to 'paid' in the database
        db.execute("UPDATE payments SET payment_status = 'paid' WHERE order_number = ?", (order_id,))
        db.connection.commit()

    return jsonify({'message': 'Notification received'}), 200


@app.route("/payment_status/<on>", methods=['POST', 'GET'])
def check_payment_status(on):

    print(on)
    status = db.execute("SELECT payment_status FROM payments WHERE order_number = ?", (on,))
    status = status.fetchone()[0]

    return jsonify({'payment_status': status})


@app.route("/orders", methods=['GET', 'POST'])
@login_required
def orders():

    if request.method == 'GET':
        # initalize orders
        orderType = request.args.get('type')
        status = request.args.get('status')
        cashValue = parseInt(session.get('cashPaid', 0))
        # get orderNumber
        payment = request.args.get('payment')
        cash = 0
        change = 0
        cart = []
        deliveryType = ""
        ftax = 0
        ftotal = 0
        tableNumber = 0
        if orderType:
            orders = db.execute("""
                SELECT orders.*, payments.payment_status
                FROM orders
                LEFT JOIN payments ON orders.order_number = payments.order_number
                WHERE DATE(order_date) = CURRENT_DATE
                AND orders.type = ?
                AND orders.status NOT IN ('completed', 'cancelled')
                ORDER BY orders.order_date ASC """, (orderType,)).fetchall()
        else:
            orders = db.execute("""
                SELECT orders.*, payments.payment_status
                FROM orders
                LEFT JOIN payments ON orders.order_number = payments.order_number
                WHERE DATE(order_date) = CURRENT_DATE
                AND orders.type = ?
                AND orders.status NOT IN ('completed', 'cancelled')
                ORDER BY orders.order_date ASC """, ('dine in',)).fetchall()

        if status:
            orders = db.execute("""
                SELECT orders.*, payments.payment_status
                FROM orders
                LEFT JOIN payments ON orders.order_number = payments.order_number
                WHERE DATE(order_date) = CURRENT_DATE
                AND orders.status = ? ORDER BY orders.order_date ASC """, (status,)).fetchall()
        if payment:
            order_details = db.execute("""
                SELECT orderitems.*, menu_list.item_name, menu_list.image_url, orders.total_amount, orders.type, orders.table_number
                FROM orderitems
                JOIN menu_list ON orderitems.item_id = menu_list.id
                JOIN orders ON orderitems.order_number = orders.order_number
                WHERE orderitems.order_number = ?
            """, (payment,)).fetchall()

            if order_details:
                total = order_details[0]['total_amount']
                tax = total / 1.1 * 0.10
                ftotal = 'Rp {:,.0f}'.format(total)
                ftax = 'Rp {:,.0f}'.format(tax)

            for item in order_details:
                cart.append({
                    'id': item['id'],
                    'order_number': item['order_number'],
                    'item_id': item['item_id'],
                    'item_quantity': item['quantity'],
                    'item_price': item['price'],
                    'total': '{:,}'.format(int(item['total'])),
                    'item_name': item['item_name'],
                    'item_image': item['image_url'],
                    'grand_total': total,
                    'deliveryType': item['type'],
                    'table_number': item['table_number']
                })
            deliveryType = cart[0]['deliveryType'].capitalize()
            tableNumber = cart[0]['table_number']

        if cart:
            session['billings'] = cart

        return render_template("orders.html", orders=orders, deliveryType=deliveryType, cart=cart, orderType=orderType, cashValue=cashValue, tax=ftax, total=ftotal, status=status, cash=cash, change=change, tableNumber=tableNumber)


@app.route("/retrieve_details", methods=['POST'])
@login_required
def retrieve_details():

    order_number = request.json['order_number']
    order_items = []

    data = db.execute("""
    SELECT orderitems.order_number, orderitems.item_id, orderitems.quantity,
           orderitems.price, orderitems.total, menu_list.item_name,
           payments.invoice_number, payments.payment_method,
           payments.payment_amount, payments.change, payments.payment_date
    FROM orderitems
    JOIN menu_list ON orderitems.item_id = menu_list.id
    JOIN payments ON orderitems.order_number = payments.order_number
    WHERE orderitems.order_number = ?
""", (order_number,)).fetchall()

    # Convert the result into a list of dictionaries
    for row in data:
        order_items.append(dict(row))

    return jsonify({'items': order_items, 'number': order_number})


@app.route("/update/<on>/<status>", methods=['POST', 'GET'])
@login_required
def update_status(on, status):

    # Fetch payment status from the database
    payment_status = db.execute('SELECT payment_status FROM payments WHERE order_number = ?', (on,)).fetchone()
    order_type = db.execute("SELECT type FROM orders WHERE order_number = ?", (on,)).fetchone()

    # Handle case where payment_status is None (no matching order)
    if payment_status is None:
        return apology("Order not found")

    # Access the payment status
    current_status = payment_status[0]
    # set current Tab
    current_Tab = order_type[0]

    # If the order is already paid and the status update is 'completed' and cancelling unpaid order
    if current_status == 'paid' and status == 'completed' or current_status == 'unpaid' and status == 'cancelled':
        db.execute("UPDATE orders SET status = ? WHERE order_number = ?", (status, on,))
        db.connection.commit()

    # If the order is paid and trying to cancel
    elif current_status == 'paid' and status == 'cancelled':
        return apology("You cannot cancel an order that has been paid")

    # If the order is unpaid and trying to complete it
    elif current_status != 'paid' and status == 'completed':
        return apology("Unable to complete an unpaid order")

    # If no valid condition is met, return a default apology
    else:
        return apology("Invalid order update request")

    return redirect(f"/orders?type={current_Tab}")


@app.route('/add_cash_paid', methods=['POST'])
@login_required
def add_cash_paid():
    data = request.json
    session['cashPaid'] = data['cashPaid']

    return jsonify({'cashPaid': session['cashPaid']})


@app.route("/complete_payment", methods=['POST', 'GET'])
@login_required
def complete_payment():
    if request.method == 'POST':
        billings = session.get('billings', [])
        payment_method = request.form.get('paymentMethod')
        order_number = billings[0]['order_number']
        totalValue = billings[0]['grand_total']
        amount = request.form.get('cashValue')
        order_type = db.execute("SELECT type FROM orders WHERE order_number = ?", (order_number,)).fetchone()
        # set current Tab
        current_Tab = order_type[0]

        if int(amount) < totalValue and payment_method == "Cash":
            flash("Invalid paid amount!", "error")
            return redirect('/orders')

        # check if payment is cash
        if payment_method == "Cash":
            # save payments to database and generate invoice
            db.execute("UPDATE payments SET payment_method = ?, payment_status = ?, payment_amount = ? WHERE order_number = ?",
                       (payment_method, "paid", amount, order_number))
            db.connection.commit()
        # check if payment is card
        if payment_method == "Card":
            db.execute("UPDATE payments SET payment_method = ?, payment_status = ?, payment_amount = ? WHERE order_number = ?",
                       (payment_method, "paid", totalValue, order_number))
            db.connection.commit()
        # check if payment is Bca Qris
        if payment_method == "BCA Qris":
            db.execute("UPDATE payments SET payment_method = ?, payment_status = ?, payment_amount = ? WHERE order_number = ?",
                       (payment_method, "paid", totalValue, order_number))
            db.connection.commit()
        if payment_method == "m-banking":
            param = bankTransfer(order_number, int(totalValue))
            charge_response = core.charge(param)
            va_number = charge_response['va_numbers'][0]['va_number']
            bank_name = charge_response['va_numbers'][0]['bank']
            db.execute("UPDATE payments SET payment_method = ?, payment_status = ?, payment_amount = ? WHERE order_number = ?",
                       (payment_method, "pending", totalValue, order_number))
            db.connection.commit()

            return render_template('payment_process.html', va_number=va_number, bank_name=bank_name, order_number=order_number, total_amount=totalValue)
        if not payment_method:
            return redirect(f"/orders?type={current_Tab}")

        session['cashPaid'] = 0
    return redirect(f"/orders?type={current_Tab}")


@app.route("/edit_order", methods=['POST', 'GET'])
@login_required
def edit_order():
    if request.method == 'GET':

        order_number = request.args.get('orders')
        cart = []
        ftotal = 0
        ftax = 0
        deliveryType = ""
        tableNumber = 0
        edit_order = True
        if order_number:
            order_details = db.execute("""
                SELECT orderitems.*, menu_list.item_name, menu_list.image_url, orders.total_amount, orders.type, orders.table_number
                FROM orderitems
                JOIN menu_list ON orderitems.item_id = menu_list.id
                JOIN orders ON orderitems.order_number = orders.order_number
                WHERE orderitems.order_number = ?
            """, (order_number,)).fetchall()

            if order_details:
                total = order_details[0]['total_amount']
                tax = total / 1.1 * 0.10
                ftotal = '{:,.0f}'.format(total)
                ftax = '{:,.0f}'.format(tax)

            for item in order_details:
                cart.append({
                    'id': item['id'],
                    'order_number': item['order_number'],
                    'item_id': item['item_id'],
                    'item_quantity': item['quantity'],
                    'item_price': '{:,}'.format(int(item['price'])),
                    'total': '{:,}'.format(int(item['total'])),
                    'item_name': item['item_name'],
                    'item_image': item['image_url'],
                    'grand_total': total,
                    'deliveryType': item['type'],
                    'table_number': item['table_number'],
                    'order_time': item['order_time']
                })
            deliveryType = cart[0]['deliveryType'].capitalize()
            tableNumber = cart[0]['table_number']
        if cart:
            session['cart'] = cart
            session['tax'] = ftax
            session['total'] = ftotal
            session['type'] = deliveryType
            session['tableNumber'] = tableNumber
            session['edit_order'] = edit_order
            session['edit_order_number'] = cart[0]['order_number']

        return redirect('/menu')
    if request.method == 'POST':
        # check if cancel button is press, itll clear out all session and go back to orders
        cancel = request.form.get('cancel')
        if cancel == 'true':
            clear_session()

            return redirect('/orders')


@app.route("/finish_edit_order", methods=['POST', 'GET'])
@login_required
def finish_edit_order():
    new_data_order = session.get('cart', 0)
    order_number = session.get('edit_order_number', 0)
    total_amount = session.get("total", 0)
    totalValue = int(str(total_amount).replace("Rp", "").replace(",", "").strip())

    # check if order_number exist in database
    existOrderNumber = db.execute("SELECT order_number FROM orders WHERE order_number = ?", (order_number,)).fetchone()
    if existOrderNumber:
        # update order total in database
        db.execute("UPDATE orders SET total_amount = ? WHERE order_number = ?", (totalValue, order_number,))
        db.connection.commit()
        # del prev items from database
        db.execute("DELETE FROM orderitems WHERE order_number = ?", (order_number,))
        db.connection.commit()
        # update orderitems in database
        for order in new_data_order:
            if 'order_time' in order:
                db.execute("INSERT INTO orderitems (order_number, item_id, quantity, price, order_time) VALUES (?, ?, ?, ?, ?)",
                           (order_number, order['item_id'], order['item_quantity'], int(order['item_price'].replace(",", "")), order['order_time']))
                db.connection.commit()
            else:
                db.execute("INSERT INTO orderitems (order_number, item_id, quantity, price, order_time) VALUES (?, ?, ?, ?, datetime('now'))",
                           (order_number, order['item_id'], order['item_quantity'], int(order['item_price'].replace(",", ""))))
                db.connection.commit()
        # update invoice amount in payments
        db.execute("UPDATE payments SET invoice_amount = ? WHERE order_number = ?", (totalValue, order_number,))
        db.connection.commit()

    # clear session
    clear_session()

    return redirect('/orders')


@app.route('/thank', methods=['POST'])
def thank():
    order_number = request.form.get('order_number')
    status = db.execute("SELECT payment_status FROM payments WHERE order_number = ?", (order_number,))
    status = status.fetchone()
    if status[0] == 'paid':
        clear_session()

        return thankYou("Your order has been successfully placed, we hope you enjoy your meal!", order_number)
    else:

        return redirect('/waiting_for_payment')


@app.route('/sync_payment/<on>', methods=['GET'])
def sync_payment(on):
    transaction_status = core.transactions.status(on)['transaction_status']
    print(transaction_status)
    # If the transaction is successful
    if transaction_status == 'settlement':
        # Update the payment status to 'paid' in the database
        db.execute("UPDATE payments SET payment_status = 'paid' WHERE order_number = ?", (on,))
        db.connection.commit()

    return redirect('/orders')

@app.route("/customization", methods=['GET'])
@login_required
def customizations():
    name = session.get('menu', 'menu')
    query = request.args.get('search')
    if query:
        main = db.execute('SELECT * FROM menu_list WHERE item_name LIKE ?', ('%' + query + '%',)).fetchall()
    else:
        main = db.execute('SELECT * FROM menu_list').fetchall()
    
    mylist = [dict(item) for item in main]
    
    categories = db.execute('SELECT DISTINCT category FROM categories').fetchall()

    return render_template('customization.html', name=name, main=main, categories=categories, query=query, mode='customize')

@app.route("/add_menu", methods=['POST'])
@login_required
def add_menu():
    if request.method == 'POST':
        session['menu'] = 'menu'
        product_title = request.form.get('title')
        product_image = request.files['image']
        product_description = request.form.get('description')
        product_price = request.form.get('price')
        product_category = request.form.get('category')
        if product_title and product_price and product_category and product_image:
            try:
                product_image_url = saveImage(product_image)
                db.execute(
                    "INSERT INTO menu_list (item_name, image_url, description, price, category) VALUES (?, ?, ?, ?, ?)",
                    (product_title, product_image_url, product_description, product_price, product_category)
                )
                db.connection.commit()
                flash("Menu item added successfully!", "success")
                return redirect('/customization')
            except Exception as e:
                flash("Error adding menu item: " + str(e), "danger")
        else:
            flash("Please fill in all fields.", "warning")
        return redirect('/customization')

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    if request.method =='POST':
        session['menu'] = 'category'
        inputCategory = request.form.get('category_title').lower()
        if inputCategory:
            try:
                db.execute("INSERT INTO categories (category) VALUES (?)", (inputCategory,))
                db.connection.commit()
            except Exception as e:
                print("Error adding category: " + str(e))
        
        return redirect('/customization')
    
@app.route('/remove_category', methods=['POST'])
@login_required
def remove_category():
    if request.method =='POST':
        session['menu'] = 'category'
        deleteCategory = request.form.get('category').lower()
        if deleteCategory:
            try:
                db.execute("DELETE FROM categories WHERE category = ?", (deleteCategory,))
                db.execute('UPDATE menu_list SET category = ? WHERE category = ?', ('Uncategorized', deleteCategory,))
                db.connection.commit()
            except Exception as e:
                print("Error adding category: " + str(e))
       
        return redirect('/customization')

@app.route('/delete_menu', methods=['GET'])
@login_required
def delete_menu():

    menu_id = request.args.get('id')
    db.execute("DELETE FROM menu_list WHERE id = ?", (menu_id, ))
    return redirect('/customization')

def saveImage(image):
    if image.filename == "":
        return "No Selected files"
    
    if image:
        # Create a safe filename
        image_path = os.path.join(current_app.root_path, 'static/images', image.filename)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        image.save(image_path)
        
    return f'/static/images/{image.filename}'

@app.route('/edit_menu', methods=['POST'])
@login_required
def edit_menu():
    if request.method == 'POST':
        id = parseInt(request.form.get('id'))
        print(id)
        name = request.form.get('item_name')
        category = request.form.get('category')
        price = request.form.get('price')
        image = request.files['image']
        if not image:
            image_url = urlparse(request.form.get('current_image')).path
        else:
            image_url = saveImage(image)
        db.execute('UPDATE menu_list SET item_name = ?, image_url = ?, price = ?, category = ? WHERE id = ?', (name, image_url, price, category, id) )
        db.connection.commit()
        return redirect('/customization')
    

@app.route('/aggregate_delete', methods=['POST'])
def aggregate_delete():
    # Get the list of selected item IDs from the POST request
    selected_ids = request.form.getlist('selected_items')
    for i in selected_ids:
        db.execute("DELETE FROM menu_list WHERE id = ?", (i, ))
        db.connection.commit()

    return redirect('/customization')

@app.route('/discount', methods=["GET"])
def discount():
    return render_template('discount.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

