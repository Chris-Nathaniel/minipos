from helpers_module.__init__ import *
from helpers_module.helpers import *
from helpers_module.models import *

def run_flask():
    
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
        # put the category into a list
        valid_categories = [row[0].title() for row in categories]

        tickets = Discount.get_active_discount_ticket()
        if query:
            # if query return the search result
            main = Menu.search_menu(query)
        elif category == 'menu':
            # if category is menu return all menu
            main = Menu.get_all_menu()
        elif category in valid_categories:
            # if category is chosen return the menu to that category
            main = Menu.search_menu_category(category)
        else:
            session['categories'] = [dict(item) for item in categories]
            return apology("oops , category not found",  code=404)
        
        if not main:
            session['category'] = category

        # initialize billing
        billing = Billing(session)
        billing.format_currency()

        return render_template("menu.html", 
            main=main, categories=categories, tickets=tickets,
            mode="menu", category=category, **billing.__dict__)


    @app.route("/login", methods=["GET", "POST"])
    def login():
        session.clear()
        """Log user in"""
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
            # if existing user exist return true and user cant register anymore
            existinguser = {user["id"]: dict(user) for user in Users.check_user()}
            if existinguser:
                existinguser = True

            return render_template("login.html", existinguser=existinguser)


    @app.route("/register", methods=["GET", "POST"])
    def register():
        
        if request.method == "POST":
            """Register user"""
            # get all users input
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
            
            # check if a user already registered, if yes log in
            existinguser = Users.check_user()
            if existinguser:
                return redirect("/login")
            else:
                Users.register(username, hashed_password)
                return redirect("/login")
        else:
            # check if a user already registered, if yes log in
            existinguser = Users.check_user()
            if existinguser:
                return redirect("/login")
            
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
        # check if cart is in session
        if 'cart' not in session:
            session['cart'] = []
        # retrieving data
        data = request.json
        # add item to cart
        Cart.update_cart_item(data, session)
        # calculate the cart total
        Cart.calculate_cart_totals(session)
        # load the billing
        billing = Billing(session)
        # Apply the discount to the new total
        billing.discount = billing.discount/100
        if billing.discount:
            billing.total = Discount.addDiscount(parseInt(billing.total), parseInt(billing.tax), billing.discount)
            session['total'] = '{:,.0f}'.format(billing.total)
            
        return jsonify({'cart': billing.cart, 'total': billing.total, 'tax': billing.tax, 'cashPaid': billing.cashValue, 'itemCount': billing.itemCount, 'voucher': billing.voucherDetail}), 200


    @app.route('/remove_from_cart', methods=['POST'])
    @login_required
    def remove_from_cart():
        # retrieving data
        data = request.json
        # remove item from cart
        Cart.remove_cart_item(data, session)
        # calculate the cart total
        Cart.calculate_cart_totals(session)
        # load the billing       
        billing = Billing(session)
        # Apply the discount to the new total
        billing.discount = billing.discount/100
        if billing.discount:
            billing.total = Discount.addDiscount(parseInt(billing.total), parseInt(billing.tax), billing.discount)
            session['total'] = '{:,.0f}'.format(billing.total)

        return jsonify({'cart': billing.cart, 'total': billing.total, 'tax': billing.tax, 'cashPaid': billing.cashValue, 'itemCount': billing.itemCount, 'voucher': billing.voucherDetail}), 200


    @app.route('/process_order', methods=['POST', 'GET'])
    @login_required
    def confirm_order():
        # load the cart
        billing = Billing(session, request.form)
        orders = billing.cart
        billing.total = parseInt(billing.total)
        # generate order number
        order_number = generate_order_number("TESTORD-")
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # handle if cashpaid is less than the invoice total and payment method is cash
        if int(billing.cashValue) < billing.total and billing.payment_method == "Cash":
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
        
        #process payments
        payment_status = Billing.process_payments(order_number, billing.payment_method, billing.total, billing.cashValue, core, current_timestamp)
        if isinstance(payment_status, dict):
                status = next(iter(payment_status), None) 
                if status == "failed":
                    return apology("There was an issue connecting to midtrans, please check your connection or your midtrans keys")
        #save the order to database
        Billing.insertOrders(orders, order_number, billing.deliveryType, billing.tableNumber, billing.total, billing.discount, current_timestamp)
        if payment_status == "success":
            clear_session()
            return thankYou("Your order has been successfully placed, we hope you enjoy your meal!", order_number)
        else:
            va_number, bank_name = payment_status
            clear_session()
            current_timestamp = datetime.now() + timedelta(hours=1)
            current_timestamp = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            Billing.insert_virtual_accounts(order_number, va_number, bank_name, billing.total, current_timestamp)
           
            return redirect(f"/waiting_for_payment/{order_number}")

    @app.route("/waiting_for_payment/<on>", methods=['GET'])
    @login_required
    def waiting_for_payment(on):
        result = Billing.search_virtual_accounts(on)
        if not result:
            Billing.revert_pending(on)
            return apology("the payment has expired")
        result = dict(result)
        va_number = result["va_number"]
        bank_name = result["bank_name"]
        order_number = result["order_number"]
        total_amount = formatCurrency("Rp", result["total_amount"])
        expiration = datetime.strptime(result["expiration"], "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        countdown = countdowndate(expiration, current_time)
        
        return render_template('payment_process.html', va_number=va_number, bank_name=bank_name, order_number=order_number, total_amount=total_amount, countdown=countdown)

    @app.route("/cancel_payment", methods=["POST"])
    @login_required
    def cancel_payment():
        on = request.form.get("order_number")
        Billing.revert_pending(on)
        return redirect("/orders")

    @app.route('/midtrans/notification', methods=['POST'])
    def midtrans_notification():
        # Get the JSON notification from Midtrans
        notification_json = request.get_json()

        # Use Midtrans library to parse and verify the notification
        notification = core.transactions.notification(notification_json)

        # Extract necessary data from the notification
        order_id = reverseFormatOrderNumber(notification['order_id'])
        transaction_status = notification['transaction_status']

        # If the transaction is successful
        if transaction_status == 'settlement':
            # Update the payment status to 'paid' in the database
            Billing.update_payment_status(order_id)

        return jsonify({'message': 'Notification received'}), 200


    @app.route("/payment_status/<on>", methods=['POST', 'GET'])
    def check_payment_status(on):
        # checking payment status
        status = Billing.check_payment_status(on)

        return jsonify({'payment_status': status})


    @app.route("/orders", methods=['GET', 'POST'])
    @login_required
    def orders():
        if request.method == 'GET':
            # initalize orders
            orderType = request.args.get('type', 'dine in')
            status = request.args.get('status')
            payment = request.args.get('payment')
            cashValue = parseInt(session.get('cashPaid', 0))
            
            # get discount tickets
            tickets = Discount.get_active_discount_ticket()

            # load the orders based on status, ordertype
            billing = Billing(session)
            billing.reset()
            if orderType:
                orders = Orders.search_orders_type(orderType)

            if status:
                orders = Orders.search_orders_status(status)
                orderType = ""
            # if payment, load the billing details and load it to the  cart
            if payment:
                order_details = Orders.fetch_order_details(payment)
                billing.cart = billing.load_order_details(order_details)

            # save the cart in session if exist
            if billing.cart:
                session['billings'] = billing.cart
                session['total'] = billing.total
                session['tax'] = billing.tax
                

            return render_template("orders.html", orders=orders, deliveryType=billing.deliveryType, cart=billing.cart, orderType=orderType, 
                                cashValue=cashValue, tax=billing.tax, total=billing.total, status=status, cash=billing.cashValue, change=billing.change, 
                                tickets=tickets, tableNumber=billing.tableNumber)


    @app.route("/retrieve_details", methods=['POST'])
    @login_required
    def retrieve_details():
        # check if request came from app gui or browser
        user_agent = request.headers.get('User-Agent', '')
        window = True if "QtWebEngine" in user_agent else False
        # get the business details if exist else return the default business details
        business = dict(Business.get_business()) if Business.get_business() else Business().__dict__
        # get the order number
        order_number = request.json['order_number']
        print(order_number)
        order_items = []
        # get the order details
        data = Orders.fetch_invoice_details(order_number)
        
        # Convert the result into a list of dictionaries
        for row in data:
            order_items.append(dict(row))

        return jsonify({'items': order_items, 'number': order_number, 'window':window, 'business':business})


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
            # load everyhingto update the payments
            billings = session.get('billings', [])
            payment_method = request.form.get('paymentMethod')
            order_number = billings[0]['order_number']
            totalValue = parseInt(billings[0]['grand_total'])
            amount = request.form.get('cashValue')
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # set current Tab
            order_type = Orders.fetch_order_details(order_number)[0]['type']
            current_Tab = order_type

            # check if cashPaid is less than total invoice
            if int(amount) < parseInt(totalValue) and payment_method == "Cash":
                flash("Invalid paid amount!", "error")
                return redirect('/orders')
            
            # check status of payment
            status = Billing.update_payments(order_number, payment_method, totalValue, amount, core, current_timestamp)
            if isinstance(status, dict):
                status = next(iter(status), None) 
                # handle if status failed
                if status == "failed":
                    return apology("There was an issue connecting to midtrans, please check your connection or your midtrans keys")
            # handle if status success
            if status != "success" and status != "not payment":
                va_number, bank_name = status
                clear_session()
                current_timestamp = datetime.now() + timedelta(hours=1)
                current_timestamp = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                Billing.insert_virtual_accounts(order_number, va_number, bank_name, totalValue, current_timestamp)
                return redirect(f"/waiting_for_payment/{order_number}")
                
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
        # check payment status
        status = Billing.check_payment_status(order_number)
        if status == 'paid':
            clear_session()

            return thankYou("Your order has been successfully placed, we hope you enjoy your meal!", order_number)
        else:
            return redirect(f'/waiting_for_payment/{order_number}')

    @app.route('/sync_payment/<on>', methods=['GET'])
    def sync_payment(on):
        on = formatOrderNumber(on) 
        try:
            transaction_status = core.transactions.status(on).get('transaction_status', None)
            
            if transaction_status == 'settlement':
                on = reverseFormatOrderNumber(on)  
                Billing.update_payment_status(on)
                flash("Payment successfully updated.", "success")
            else:
                flash(f"Payment status: {transaction_status}", "info")

        except Exception as e:
            logging.error(f"Error syncing payment for order {on}: {str(e)}")
            flash("An error occurred while syncing payment.", "danger")
            

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
            session['menu_choice'] = 'Add Menu'
            # get the input request
            product_title = request.form.get('title')
            product_image = request.files['image']
            product_description = request.form.get('description')
            product_price = request.form.get('price')
            product_category = request.form.get('category')
            # insert product if exist
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
        session['menu_choice'] = 'Add Category'  
        # get input from category
        inputCategory = request.form.get('category_title').lower()
        # insert category if exist
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
        session['menu_choice'] = 'Add Category'  
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

    @app.route('/edit_menu', methods=['POST'])
    @login_required
    def edit_menu():
        if request.method == 'POST':
            session['menu_choice'] = 'Edit Menu'
            id = parseInt(request.form.get('id'))
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
            # get discount inpu
            title = request.form.get('title')
            discount = request.form.get('discAmount')
            description = request.form.get('discDescription')
            expiration = request.form.get('discExpiration')
            discountCode = generate_random_string().upper()
            imageUrl = createImageUrl("https://www.casacenina.com/catalog/images/img_192/rico-99000-0421.jpg", f'{discount}% off')

            # insert discount voucher to database
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
        session['voucherDetail'] = data
        session['discount'] = int(data['discount'])
        discount = session['discount']/100
        total = parseInt(session.get('total', 0))
        print(total)
        tax = parseInt(session.get('tax', 0))
        print(tax)
        discountedTotal = Discount.addDiscount(total, tax, discount)
        session['total'] = '{:,.0f}'.format(discountedTotal)

        return jsonify({'discountValue': session['discount'], 'discountedTotal': discountedTotal})
    
    @app.route("/removeDiscount", methods=['POST'])
    def removeDiscount():
        discount = parseInt(session.get('discount', ""))/100
        total = parseInt(session.get('total', 0))
        tax = parseInt(session.get('tax', 0))
        originalTotal = Discount.removeDiscount(total, tax, discount)
        session['total'] = '{:,.0f}'.format(originalTotal)
        session.pop('discount', None)
        session.pop('voucherDetail', None)
        return jsonify({
        "message": "Discount removed successfully",
        "originalTotal": originalTotal
    })
    
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
        # get all business details input from form
        business_name = request.form.get("businessName")
        business_address = request.form.get("businessAddress")
        business_contact = request.form.get("businessContact")
        business_email = request.form.get("businessEmail")
        emailer = Emailer(business_email)
        business = Business(business_name, business_address, business_contact, business_email)
        if Business.get_business():
            # if exist update business
            business.update_business()
        else:
            # if not exist insert business
            business.insert_business()
        flash("business settings has been updated!")
        emailer.send_registration_email(business_name)
        return redirect("/settings")
    
    @app.route("/midtrans-integration", methods=["POST"])
    @login_required
    def midtransIntegration():
        # get the input from request
        clk, svk = request.form.get("clk"), request.form.get('svk')
        dotenv_path = '.env'
        if not os.path.exists(dotenv_path):
            with open(dotenv_path, 'w') as f:
                f.write("") 
        set_key(dotenv_path, 'PUBLIC_CLIENT', clk)
        set_key(dotenv_path, 'SERVER_KEY', svk)
        # set key in environmental variable
        os.environ['PUBLIC_CLIENT'] = clk
        os.environ['SERVER_KEY'] = svk
        flash("Conecting to Midtrans, Please restart the app again to apply the changes!")
        return redirect("/settings#mdi")
    
    @app.route("/ngrok-settings", methods=["POST"])
    @login_required
    def ngrok_setup():
        # get input from request
        domain, auth = request.form.get("domain"), request.form.get('auth')
        dotenv_path = '.env'
        if not os.path.exists(dotenv_path):
            with open(dotenv_path, 'w') as f:
                f.write("") 
        # set key in environmental variable
        set_key(dotenv_path, 'NGROK_DOMAIN', domain)
        set_key(dotenv_path, 'NGROK_AUTH', auth)
        os.environ['NGROK_DOMAIN'] = domain
        os.environ['NGROK_AUTH'] = auth
        flash("You are now connected, your app is now available at that domain. Don't forget to place the domain on midtrans to start receiving notifications.")
        return redirect("/settings#ngrk")
    
    @app.route("/delete-database", methods=["POST"])
    @login_required
    def reset_database():
        oldDataBase = os.getenv("OLD_DB_URL", "")
        name = generate_name()
        if oldDataBase:
            if oldDataBase and oldDataBase.endswith(".db"):
                db_path = secure_filename(oldDataBase) 
                if os.path.exists(db_path):
                    os.remove(db_path)
        
        # Run the batch script to regenerate the database
        # subprocess.run([r'scripts\dbgenerator.bat', name], shell=True) --> depreciated
        db_name = create_database(name)
        update_env(db_name)
        flash("You need to restart the app to apply the changes.")
        return redirect("/settings")
    
    @app.route("/resetpwdrequest", methods=["GET", "POST"])
    def password_reset():
        if request.method == "POST":
            token = request.args.get('token')
            # check token if exist in database
            dbtoken = Emailer.search_token(token)
            if not dbtoken:
                flash("Token has expired, please request another from email!")
            else:
                # get the users new password
                password = request.form.get('new_password')
                confirmation = request.form.get('confirm_password')
                if not password:
                    return apology("Password is required!")
                if password == confirmation:
                    hashed_password = generate_password_hash(password)
                else:
                    return apology("please confirm password")
                Users.reset_password(hashed_password)
                flash("Password has been changed!")
                
        return render_template("password_reset.html")
    
    @app.route("/pwdemailconfirmation", methods=["GET", "POST"])
    def pwdemailconfirmation():
        if request.method == "POST":
            # check if the email is registered send link
            email = request.form.get("email")
            try:
                # Check if email is registered
                email = dict(Business.check_email(email))

                # Generate secure token and expiration time
                token = secrets.token_urlsafe(32)   
                expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)

                # Store in password_reset table
                db.execute("INSERT INTO password_reset (business_id, token, expiration) VALUES (?, ?, ?)", (email['id'], token, expiration))
                db.connection.commit()
                
                # Generate password reset link url
                reset_link = url_for('password_reset', token=token, _external=True)
                
                # send email with link to reset password
                emailer = Emailer(email['email'])
                emailer.send_password_reset(email['name'], reset_link)
                flash("Password reset link has been sent to your email.")

            except Exception as e:
                flash(f"Email not found")

        return render_template("email_confirmation.html")
    
    @app.route("/receive-html", methods=["POST", "GET"])
    def receive_html():
        if request.method == "POST":
            # get the data from request
            data = request.get_json()
            business = dict(Business.get_business()) if Business.get_business() else Business()
            receipt = data['orderitems']
            print(receipt)
            cls = data['cls']
            cls = Ticket if cls == 'view' else Receipt
            # load the print window and receipt/ticket
            multiprocessing.Process(target=Printable.printer_window, args=(cls,receipt, business)).start()
            # Send a success response
            return jsonify({"message": "HTML received successfully"}), 200
        
    #ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    # Run Flask in a separate thread
    threading.Thread(target=connect_ngrok, daemon=True).start()
    threading.Thread(target=run_flask, daemon=True).start() if gui else run_flask()
    
    # Run the PyQt6 GUI
    MainWindow.run_gui() if gui else None