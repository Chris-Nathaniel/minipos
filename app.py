from flask import Flask, render_template, request, session, redirect, flash, jsonify, current_app, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from conn import SQL, init_app
from models import Menu, Discount, Users, Billing, Orders, Cart, Business, MainWindow, Ev
from helpers import apology, login_required, thankYou, parseInt, formatCurrency, bankTransfer, generate_order_number, clear_session, generate_random_string, createImageUrl, mask_key, set_key
import os
import ctypes
import threading


def run_flask():
    
    app = Flask(__name__)

    # Initialize the app with environment variables and Midtrans client
    core, database_url = init_app(app)
    # connect to database
    db = SQL(database_url)
    
    @app.route('/')
    @login_required
    def choose_option():
        if Business.get_business():
            business_name = Business.get_business()['name']
        else:
            business_name = "Sleeping Giant Inn"
        if 'dinein' in request.args:
            # Handle the Take Away option
            session['type'] = "dine in"
            return redirect('/menu')
        if 'takeout' in request.args:
            # Handle the Dine In option
            session['type'] = "take out"
            return redirect('/menu')

        return render_template('index.html', business_name=business_name)

    @app.route("/<category>")
    @login_required
    def menu_by_category(category):
        # check if customer have chosen order type
        if 'type' not in session or not session['type']:
            return redirect("/")

        query = request.args.get('search')
        # fetch menu list by category
        categories = Menu.get_category()
        valid_categories = [row[0].title() for row in categories]

        tickets = Discount.get_active_discount_ticket()
        if query:
            main = Menu.search_menu(query)
        elif category == 'menu':
            main = Menu.get_all_menu()
        elif category in valid_categories:
            main = Menu.search_menu_category(category)
        else:
            session['categories'] = [dict(item) for item in categories]
            return apology("oops , category not found",  code=404)
        
        if not main:
            session['category'] = category

        billing = Billing(session)
        billing.format_currency()

        return render_template("menu.html", 
            main=main, categories=categories, tickets=tickets,
            mode="menu", category=category, **billing.__dict__)


    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in"""
        session.clear()

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", code=402)

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", code=402)

            # Query database for username
            rows = Users.search_username(request.form.get("username"))

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                return apology("invalid username and/or password", code=402)

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
                return apology("Password is required!")
            if password == confirmation:
                hashed_password = generate_password_hash(password)
            else:
                return apology("please confirm password")

            # check if user already registered, if not registered
            existinguser = Users.search_username(username)
            if existinguser:
                return apology("user already registered", code=400)
            else:
                Users.register(username, hashed_password)
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
        # retrieving data
        data = request.json
        Cart.update_cart_item(data, session)
        Cart.calculate_cart_totals(session)
        cash = session.get('cashPaid', 0)

        return jsonify({'cart': session['cart'], 'total': session['total'], 'tax': session['tax'], 'cashPaid': cash, 'itemCount': session['itemCount']}), 200


    @app.route('/remove_from_cart', methods=['POST'])
    @login_required
    def remove_from_cart():
        data = request.json
        Cart.remove_cart_item(data, session)
        Cart.calculate_cart_totals(session)
        cash = session.get('cashPaid', 0)

        return jsonify({'cart': session['cart'], 'total': session['total'], 'tax': session['tax'], 'cashPaid': cash, 'itemCount': session['itemCount']}), 200


    @app.route('/process_order', methods=['POST', 'GET'])
    @login_required
    def confirm_order():

        orders = session.get("cart", [])
        billing = Billing(session, request.form)
        totalValue = parseInt(billing.total)
        order_number = generate_order_number("TESTORD-")
        
        if int(billing.cashValue) < totalValue and billing.payment_method == "Cash":
            flash("Invalid paid amount!", "error")
            return redirect('/menu')

        # check if orders is empty
        if not orders:
            return redirect("/")
        if not billing.tableNumber:
            billing.tableNumber = 0
        if billing.deliveryType == "take out" and not billing.payment_method:
            flash("Error: Takeaway orders must provide a payment method", "error")
            return redirect("/menu")

        #save the order to database
        Billing.insertOrders(orders, order_number, billing.deliveryType, billing.tableNumber, billing.total, billing.discount)
        #process payments
        payment_status = Billing.process_payments(order_number, billing.payment_method, billing.total, billing.cashValue, core)
        if isinstance(payment_status, dict):
                status = next(iter(status), None) 
                if status == "failed":
                    return apology("There was an issue connecting to midtrans, please check your connection or your midtrans keys")
        if payment_status == "success":
            clear_session()
            return thankYou("Your order has been successfully placed, we hope you enjoy your meal!", order_number)
        else:
            va_number, bank_name = payment_status
            clear_session()
            session['va_number'] = va_number
            session['bank_name'] = bank_name
            session['order_number'] = order_number
            session['total_amount'] = billing.total

            return redirect("/waiting_for_payment")

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
            Billing.update_payment_status(order_id)

        return jsonify({'message': 'Notification received'}), 200


    @app.route("/payment_status/<on>", methods=['POST', 'GET'])
    def check_payment_status(on):
        print(on)
        status = Billing.check_payment_status(on)

        return jsonify({'payment_status': status})


    @app.route("/orders", methods=['GET', 'POST'])
    @login_required
    def orders():
        if request.method == 'GET':
            # initalize orders
            orderType = request.args.get('type', 'dine in')
            status = request.args.get('status')
            cashValue = parseInt(session.get('cashPaid', 0))
            payment = request.args.get('payment')
            tickets = Discount.get_active_discount_ticket()
            billing = Billing(session)
            billing.reset()
            if orderType:
                orders = Orders.search_orders_type(orderType)

            if status:
                orders = Orders.search_orders_status(status)
                orderType = ""

            if payment:
                order_details = Orders.fetch_order_details(payment)
                billing.cart = billing.load_order_details(order_details)

            if billing.cart:
                session['billings'] = billing.cart

            return render_template("orders.html", orders=orders, deliveryType=billing.deliveryType, cart=billing.cart, orderType=orderType, 
                                cashValue=cashValue, tax=billing.tax, total=billing.total, status=status, cash=billing.cashValue, change=billing.change, 
                                tickets=tickets, tableNumber=billing.tableNumber)


    @app.route("/retrieve_details", methods=['POST'])
    @login_required
    def retrieve_details():

        order_number = request.json['order_number']
        order_items = []

        data = Orders.fetch_invoice_details(order_number)

        # Convert the result into a list of dictionaries
        for row in data:
            order_items.append(dict(row))

        return jsonify({'items': order_items, 'number': order_number})


    @app.route("/update/<on>/<status>", methods=['POST', 'GET'])
    @login_required
    def update_status(on, status):

        # Fetch payment status from the database
        payment_status = Billing.check_payment_status(on)
        order_type = Orders.fetch_order_details(on)[0]['type']


        # Handle case where payment_status is None (no matching order)
        if payment_status is None:
            return apology("Order not found",code=404)

        # Access the payment status
        current_status = payment_status
        # set current Tab
        current_Tab = order_type

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
            totalValue = parseInt(billings[0]['grand_total'])
            amount = request.form.get('cashValue')
            order_type = Orders.fetch_order_details(order_number)[0]['type']

            # set current Tab
            current_Tab = order_type

            if int(amount) < parseInt(totalValue) and payment_method == "Cash":
                flash("Invalid paid amount!", "error")
                return redirect('/orders')
            status = Billing.update_payments(order_number, payment_method, totalValue, amount, core)
            if isinstance(status, dict):
                status = next(iter(status), None) 
                if status == "failed":
                    return apology("There was an issue connecting to midtrans, please check your connection or your midtrans keys")
            if status != "success" and status != "not payment":
                va_number, bank_name = status
                return render_template('payment_process.html', va_number=va_number, bank_name=bank_name, order_number=order_number, total_amount=totalValue)
                
            session['cashPaid'] = 0
        return redirect(f"/orders?type={current_Tab}")


    @app.route("/edit_order", methods=['POST', 'GET'])
    @login_required
    def edit_order():
        if request.method == 'GET':
            clear_session()
            order_number = request.args.get('orders')
            billing = Billing(session)
            edit_order = True
            if order_number:
                order_details = Orders.fetch_order_details(order_number)
                billing.load_order_details(order_details)
                
            if billing.cart:
                session['cart'] = billing.cart
                session['tax'] = billing.tax
                session['total'] = billing.total
                session['type'] = billing.deliveryType
                session['tableNumber'] = billing.tableNumber
                session['edit_order'] = edit_order
                session['edit_order_number'] = billing.cart[0]['order_number']

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
        existOrderNumber = Orders.search_orders_number(order_number)
        if existOrderNumber:
            # update order total in database
            Orders.update_orders_total(totalValue, order_number)
            # del prev items from database
            Orders.delete_orderitems(order_number)
            # update orderitems in database
            Orders.update_order_items(new_data_order, order_number)
            # update invoice amount in payments
            Billing.update_invoice(totalValue, order_number)

        # clear session
        clear_session()

        return redirect('/orders')


    @app.route('/thank', methods=['POST'])
    def thank():
        order_number = request.form.get('order_number')
        status = Billing.check_payment_status(order_number)
        if status == 'paid':
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
            Billing.update_payment_status(on)

        return redirect('/orders')


    @app.route("/customization", methods=['GET'])
    @login_required
    def customizations():
        name = session.get('menu', 'menu')
        query = request.args.get('search')
        if query:
            main = Menu.search_menu(query)
        else:
            main = Menu.get_all_menu()

        mylist = [dict(item) for item in main]

        categories = Menu.get_category()

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
                    Menu.add_menu(product_title, product_image_url, product_description, product_price, product_category)
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
        session['menu'] = 'category'
        session['menu_choice'] = 'Add Category'  # Store the selected menu choice
        inputCategory = request.form.get('category_title').lower()
        if inputCategory:
            try:
                Menu.add_category(inputCategory)
            except Exception as e:
                print("Error adding category: " + str(e))
        return redirect('/customization')


    @app.route('/remove_category', methods=['POST'])
    @login_required
    def remove_category():
        session['menu'] = 'category'
        session['menu_choice'] = 'Add Category'  # Store the selected menu choice
        deleteCategory = request.form.get('category').lower()
        if deleteCategory:
            try:
                Menu.remove_category(deleteCategory)
            except Exception as e:
                print("Error removing category: " + str(e))
        return redirect('/customization')



    @app.route('/delete_menu', methods=['GET'])
    @login_required
    def delete_menu():

        menu_id = request.args.get('id')
        Menu.delete_menu(menu_id)
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
            Menu.update_menu(name, image_url, price, category, id)
            return redirect('/customization')


    @app.route('/aggregate_delete', methods=['POST'])
    @login_required
    def aggregate_delete():
        # Get the list of selected item IDs from the POST request
        selected_ids = request.form.getlist('selected_items')
        for i in selected_ids:
            Menu.delete_menu(i)

        return redirect('/customization')


    @app.route('/discount', methods=["GET", "POST"])
    @login_required
    def discount():
        if request.method == "POST":
            title = request.form.get('title')
            discount = request.form.get('discAmount')
            description = request.form.get('discDescription')
            expiration = request.form.get('discExpiration')
            discountCode = generate_random_string().upper()
            imageUrl = createImageUrl("https://www.casacenina.com/catalog/images/img_192/rico-99000-0421.jpg", f'{discount}% off')

            try:
                Discount.insert_discount(title, description, discount, expiration, discountCode, imageUrl)
            except Exception as e:
                return "Error inserting data into the database", 500

            tickets = Discount.get_active_discount_ticket()

            return render_template('discount.html', tickets=tickets)
        if request.method == "GET":
            query = request.args.get('codeSearch')
            if query:
                tickets = Discount.search_discount_ticket(query)

            else:
                tickets = Discount.get_active_discount_ticket()

            return render_template('discount.html', tickets=tickets)


    @app.route('/searchVoucher', methods=['POST'])
    def search_voucher():
        code = request.json.get('code')

        # Query the database for matching tickets
        if code:
            tickets = Discount.search_discount_ticket(code)

        else:
            tickets = Discount.get_active_discount_ticket()

        # Convert the rows into dictionaries
        tickets_list = [dict(ticket) for ticket in tickets]

        return jsonify({'tickets': tickets_list})


    @app.route('/addDiscount', methods=['POST'])
    def addDiscount():
        data = request.json
        session['discount'] = int(data['discount'])
        discount = session['discount']/100
        total = parseInt(session.get('total', 0))
        tax = parseInt(session.get('tax', 0))
        discountedTotal = int(total - ((total - tax)*discount))
        session['total'] = '{:,.0f}'.format(discountedTotal)

        return jsonify({'discountValue': session['discount'], 'discountedTotal': discountedTotal})
    
    @app.route("/settings", methods=['GET'])
    @login_required
    def settings():
        business_details = Business.get_business()
        ev =Ev()
        masked = {key: mask_key(value) if key in ['clkey', 'svkey', 'ngauth'] else value 
                for key, value in ev.__dict__.items()}

        return render_template("settings.html", business_details=business_details, masked=masked)
    
    @app.route("/business-settings", methods=['POST'])
    @login_required
    def businessdetails():
        business_name = request.form.get("businessName")
        business_address = request.form.get("businessAddress")
        business_contact = request.form.get("businessContact")
        business_email = request.form.get("businessEmail")
        business = Business(business_name, business_address, business_contact, business_email)
        if Business.get_business():
            business.update_business()
        else:
            business.insert_business()
        flash("business settings has been updated!")
        return redirect("/settings")
    
    @app.route("/midtrans-integration", methods=["POST"])
    @login_required
    def midtransIntegration():
        clk, svk = request.form.get("clk"), request.form.get('svk')
        dotenv_path = '.env'
        if not os.path.exists(dotenv_path):
            with open(dotenv_path, 'w') as f:
                f.write("") 
        set_key(dotenv_path, 'PUBLIC_CLIENT', clk)
        set_key(dotenv_path, 'SERVER_KEY', svk)
        os.environ['PUBLIC_CLIENT'] = clk
        os.environ['SERVER_KEY'] = svk
        
        return redirect("/settings")
    
    @app.route("/ngrok-settings", methods=["POST"])
    @login_required
    def ngrok_setup():
        domain, auth = request.form.get("domain"), request.form.get('auth')
        print(domain, auth)
        dotenv_path = '.env'
        if not os.path.exists(dotenv_path):
            with open(dotenv_path, 'w') as f:
                f.write("") 
        set_key(dotenv_path, 'NGROK_DOMAIN', domain)
        set_key(dotenv_path, 'NGROK_AUTH', auth)
        os.environ['NGROK_DOMAIN'] = domain
        os.environ['NGROK_AUTH'] = auth
        
        return redirect("/settings")

    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    # Run Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Run the PyQt6 GUI
    MainWindow.run_gui()
