from conn import *
from helpers_module.helpers import *
from helpers_module.__init__ import *


class Business:
    def __init__(self, name, address, contact, email):
        self.name = name
        self.address = address
        self.contact = contact
        self.email = email

    def insert_business(self):
        db.execute("INSERT INTO business (name, address, contact, email) VALUES(?, ?, ?, ?)", (
            self.name, self.address, self.contact, self.email))
        db.connection.commit()
  
    def get_business():
        # Check if the business exists in the database
        result = db.execute("SELECT * FROM business WHERE id = 1").fetchone()
        return result
    
    def update_business(self):
        db.execute("UPDATE business SET name = ?, address = ?, contact = ?, email = ? WHERE id = 1", 
                   (self.name, self.address, self.contact, self.email))
        db.connection.commit()

    def check_email(input):
        return db.execute("SELECT * FROM business WHERE email = ?", (input,)).fetchone()
    
class Menu:
    def get_all_menu():
        return db.execute('SELECT * FROM menu_list').fetchall()
    
    def get_category():
        return db.execute('SELECT DISTINCT category FROM categories').fetchall()
    
    def search_menu(query):
        return db.execute('SELECT * FROM menu_list WHERE item_name LIKE ?',
                          ('%' + query + '%',)).fetchall()
    
    def search_menu_category(category):
        return db.execute('SELECT * FROM menu_list WHERE category Like ?', (category,)).fetchall()
    
    def add_menu(product_title, product_image_url, product_description, product_price, product_category):
        db.execute(
                    "INSERT INTO menu_list (item_name, image_url, description, price, category) VALUES (?, ?, ?, ?, ?)",
                    (product_title, product_image_url, product_description, product_price, product_category)
                )
        db.connection.commit()
    
    def delete_menu(menu_id):
        db.execute("DELETE FROM menu_list WHERE id = ?", (menu_id, ))

    def add_category(category):
        db.execute("INSERT INTO categories (category) VALUES (?)", (category,))
        db.connection.commit()     
    
    def remove_category(category):
        db.execute("DELETE FROM categories WHERE category = ?", (category,))
        db.execute('UPDATE menu_list SET category = ? WHERE category = ?',
                    ('Uncategorized', category,))
        db.connection.commit()

    def update_menu(name, image_url, price, category, id):
        db.execute('UPDATE menu_list SET item_name = ?, image_url = ?, price = ?, category = ? WHERE id = ?',
                   (name, image_url, price, category, id))
        db.connection.commit()

class Discount:
    def get_active_discount_ticket():
        return db.execute("SELECT * FROM discount_ticket WHERE expiration_date > datetime('now')").fetchall()
    
    def search_discount_ticket(code):
        return db.execute("SELECT * FROM discount_ticket WHERE expiration_date > datetime('now') AND discount_code = ?", (code,)).fetchall()
    
    def insert_discount(title, description, discount, expiration, discountCode, imageUrl):
        db.execute("INSERT INTO discount_ticket (title, description, discount, expiration_date, discount_code, image ) VALUES (?, ?, ?, ?, ?, ?)",
                       (title, description, discount, expiration, discountCode, imageUrl))
        db.connection.commit()
    
    def addDiscount(total, tax, discount):
        discountedTotal = int(total - ((total - tax)*discount))
        return discountedTotal

    def removeDiscount(total, tax, discount):
        originalTotal = int(total - (tax*discount))/(1-discount)
        return originalTotal
    
class Users:
    def check_user():
        return db.execute("SELECT * FROM users").fetchall()
    
    def search_username(username):
        return db.execute("SELECT * FROM users WHERE username = ?",
                          (username,)).fetchall()
    def search_username_byid(id):
        return db.execute('SELECT username FROM users WHERE id = ?',
                          (id,)).fetchone()
    def register(username, password):
        db.execute("INSERT INTO users (username, hash) VALUES (?,?)",
                       (username, password,))
        db.connection.commit()
    
    def reset_password(password):
        db.execute("UPDATE Users SET hash = ? WHERE id = 1", (password, ))
        db.connection.commit()

class Cart:
    def update_cart_item(data, session):
        """ Updates the cart by incrementing item quantity or adding a new item. """
        for item in session.get('cart', []): 
            if item['item_id'] == data['item_id']:
                item['item_quantity'] = str(int(item['item_quantity']) + 1)
                return  
        session['cart'].append(data)

    def remove_cart_item(data, session):
        """ Removes an item from the cart based on `item_id` and optional `ordertime`. """
        if data['ordertime'] == 'undefined':
            del data['ordertime']
        
        session['cart'] = [
            item for item in session.get('cart', []) 
            if str(item.get('item_id')) != data.get('item_id') or item.get('order_time') != data.get('ordertime')
        ]

    def calculate_cart_totals(session):
        """ Calculates total cost, tax, and item count in the cart. """
        gtotal, itemCount = 0, 0
        for item in session.get('cart', []):  
            total = int(item['item_price'].replace(',', '')) * int(item['item_quantity'])
            item['total'] = '{:,.0f}'.format(total)
            gtotal += total
            itemCount += int(item['item_quantity'])
        
        session.update({
            'tax': '{:,.0f}'.format(gtotal * 0.10),
            'total': '{:,.0f}'.format(gtotal + gtotal * 0.10),
            'itemCount': itemCount
        })
    
class Billing:
    def __init__(self, session, form=None):
        self.cart = session.get('cart', [])
        self.total = session.get('total', 0)
        self.tax = session.get('tax', 0)
        self.cashValue = session.get('cashPaid', 0)
        self.tableNumber = session.get('tableNumber', "")
        self.deliveryType = session.get('type', 'cart')
        self.finish_edit_order = session.get('edit_order', '')
        self.change = parseInt(self.cashValue) - parseInt(self.total)
        self.discount = session.get('discount', 0)
        self.voucherDetail = session.get('voucherDetail', "")
        self.itemCount = session.get("itemCount", 0)

        if form:
            self.payment_method = form.get('paymentMethod')
            self.tableNumber = form.get('table')
            self.cashValue = form.get('cashValue')
            
    def format_currency(self):
        self.total = parseInt(self.total)
        self.tax = parseInt(self.tax)
        self.cashValue = parseInt(self.cashValue)
        self.deliveryType = self.deliveryType.capitalize()
        if self.total not in ['0', 0]:
            self.tax = formatCurrency("Rp", self.tax)
            self.total = formatCurrency("Rp", self.total)

        if self.cashValue not in ['0', 0]:
            self.cash = formatCurrency("Rp", self.cashValue)
            self.change = formatCurrency("Rp", self.change)
        else:
            self.change = 0
            self.cash = self.cashValue
    
    def insertOrders(orders, orderNumber, deliveryType, tableNumber, total, discount):
        # save order to database
        result = db.execute("INSERT INTO orders (order_number, type, table_number, status, total_amount, discount) VALUES (?, ?, ?, ?, ?, ?) RETURNING order_number, order_date",
                        (orderNumber, deliveryType, tableNumber, "new", total, discount,)).fetchone()
        
        # Fetch the returned order number and order_date
        order_number, order_date = result

        # save order items to database
        for order in orders:
            db.execute("INSERT INTO orderitems (order_number, item_id, quantity, price, order_time) VALUES (?, ?, ?, ?, ?)",
                    (order_number, order['item_id'], order['item_quantity'], int(order['item_price'].replace(",", "")), order_date))
            db.connection.commit()
        

    def process_payments(orderNumber, paymentMethod, total, cashValue, core):
        # check if payment is cash
        if paymentMethod == "Cash":
        # save payments to database and generate invoice
            db.execute("INSERT INTO payments (order_number, payment_method, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?, ?)",
                    (orderNumber, paymentMethod, "paid", total, cashValue))
            db.connection.commit()
            return "success"
        # check if payment is card
        if paymentMethod == "Card":
            db.execute("INSERT INTO payments (order_number, payment_method, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?, ?)",
                    (orderNumber, paymentMethod, "paid", total, total))
            db.connection.commit()
            return "success"
        # check if payment is Bca Qris
        if paymentMethod == "BCA Qris":
            db.execute("INSERT INTO payments (order_number, payment_method, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?, ?)",
                    (orderNumber, paymentMethod, "paid", total, total ))
            db.connection.commit()
            return "success"
        # check if payment is m-banking
        if paymentMethod == "m-banking":
            formattedordernumber = formatOrderNumber(orderNumber)
            param = bankTransfer(formattedordernumber, total)
            try:
                charge_response = core.charge(param)
            except Exception as e:
                message = {"failed": e}
                return message    
            va_number = charge_response['va_numbers'][0]['va_number']
            bank_name = charge_response['va_numbers'][0]['bank']
            db.execute("INSERT INTO payments (order_number, payment_method, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?, ?)",
                    (orderNumber, paymentMethod, "pending", total, total))
            db.connection.commit()
            return va_number, bank_name
        if not paymentMethod:
            db.execute("INSERT INTO payments (order_number, payment_status, invoice_amount, payment_amount) VALUES (?, ?, ?, ?)",
                    (orderNumber, "unpaid", total, 0,))
            db.connection.commit()
            return "success"
        
    def update_payments(order_number, payment_method, totalValue, cashValue, core):
        # check if payment is cash
        if payment_method == "Cash":
            # save payments to database and generate invoice
            db.execute("UPDATE payments SET payment_method = ?, payment_status = ?, payment_amount = ? WHERE order_number = ?",
                       (payment_method, "paid", cashValue, order_number))
            db.connection.commit()
            return "success"
        
        # check if payment is card
        if payment_method == "Card":
            db.execute("UPDATE payments SET payment_method = ?, payment_status = ?, payment_amount = ? WHERE order_number = ?",
                       (payment_method, "paid", totalValue, order_number))
            db.connection.commit()
            return "success"
        
        # check if payment is Bca Qris
        if payment_method == "BCA Qris":
            db.execute("UPDATE payments SET payment_method = ?, payment_status = ?, payment_amount = ? WHERE order_number = ?",
                       (payment_method, "paid", totalValue, order_number))
            db.connection.commit()
            return "success"
        if payment_method == "m-banking":
            param = bankTransfer(order_number, int(totalValue))
            try:
                charge_response = core.charge(param)
            except Exception as e:
                message = {"failed": e}
                return message    
            va_number = charge_response['va_numbers'][0]['va_number']
            bank_name = charge_response['va_numbers'][0]['bank']
            db.execute("UPDATE payments SET payment_method = ?, payment_status = ?, payment_amount = ? WHERE order_number = ?",
                       (payment_method, "pending", totalValue, order_number))
            db.connection.commit()

            return va_number, bank_name
        if not payment_method:
            return "not payment"
        
    def update_invoice(totalValue, orderNumber):
        db.execute("UPDATE payments SET invoice_amount = ? WHERE order_number = ?",
                   (totalValue, orderNumber,))
        db.connection.commit()

    def load_order_details(self, order_details):
        # load order details from database
        if order_details:
                self.total = order_details[0]['total_amount']
                self.tax = self.total / 1.1 * 0.10
                self.total = 'Rp {:,.0f}'.format(self.total)
                self.tax = 'Rp {:,.0f}'.format(self.tax)

        for item in order_details:
            self.cart.append({
                'id': item['id'],
                'order_number': item['order_number'],
                'item_id': item['item_id'],
                'item_quantity': item['quantity'],
                'item_price': '{:,}'.format(int(item['price'])),
                'total': '{:,}'.format(int(item['total'])),
                'item_name': item['item_name'],
                'item_image': item['image_url'],
                'grand_total': self.total,
                'deliveryType': item['type'],
                'table_number': item['table_number'],
                'order_time': item['order_time']
            })

        self.deliveryType = self.cart[0]['deliveryType'].capitalize()
        self.tableNumber = self.cart[0]['table_number']
        return self.cart
    
    def check_payment_status(orderNumber):
        status = db.execute("SELECT payment_status FROM payments WHERE order_number = ?", (orderNumber,)).fetchone()[0]
        return status
    
    def update_payment_status(orderNumber):
        db.execute("UPDATE payments SET payment_status = 'paid' WHERE order_number = ?", (orderNumber,))
        db.connection.commit()

    def reset(self):
        self.cashValue = 0
        self.change = 0
        self.cart = []
        self.deliveryType = ""
        self.tax = 0
        self.total = 0
        self.tableNumber = 0

class Orders:
    def search_orders_number(orderNumber):
        return db.execute("SELECT * FROM orders WHERE order_number = ?", (orderNumber,)).fetchone()
    
    def search_orders_type(orderType):
        return db.execute("""
                SELECT orders.*, payments.payment_status
                FROM orders
                LEFT JOIN payments ON orders.order_number = payments.order_number
                WHERE DATE(order_date) = CURRENT_DATE
                AND orders.type = ?
                AND orders.status NOT IN ('completed', 'cancelled')
                ORDER BY orders.order_date ASC """, (orderType,)).fetchall()
    
    def search_orders_status(status):
        return db.execute("""
                SELECT orders.*, payments.payment_status
                FROM orders
                LEFT JOIN payments ON orders.order_number = payments.order_number
                WHERE DATE(order_date) = CURRENT_DATE
                AND orders.status = ? ORDER BY orders.order_date ASC """, (status,)).fetchall()
    
    def fetch_order_details(orderNumber):
        return db.execute("""
            SELECT orderitems.*, menu_list.item_name, menu_list.image_url, orders.total_amount, orders.type, orders.table_number
            FROM orderitems
            JOIN menu_list ON orderitems.item_id = menu_list.id
            JOIN orders ON orderitems.order_number = orders.order_number
            WHERE orderitems.order_number = ?
            """, (orderNumber,)).fetchall()
        
    def fetch_invoice_details(orderNumber):
        return db.execute("""
            SELECT orderitems.order_number, orderitems.item_id, orderitems.quantity,
                orderitems.price, orderitems.total, menu_list.item_name,
                payments.invoice_number, payments.payment_method,
                payments.payment_amount, payments.change, payments.payment_date, orders.total_amount, orders.discount
            FROM orderitems
            JOIN menu_list ON orderitems.item_id = menu_list.id
            JOIN payments ON orderitems.order_number = payments.order_number
            JOIN orders ON orderitems.order_number = orders.order_number
            WHERE orderitems.order_number = ?
            """, (orderNumber,)).fetchall()
    
    def update_orders_total(totalValue, order_number):
        db.execute("UPDATE orders SET total_amount = ? WHERE order_number = ?",
                   (totalValue, order_number,))
        db.connection.commit()
    
    def delete_orderitems(orderNumber):
        db.execute("DELETE FROM orderitems WHERE order_number = ?", (orderNumber,))
        db.connection.commit()

    def update_order_items(cart, orderNumber):
        for order in cart:
            if 'order_time' in order:
                db.execute("INSERT INTO orderitems (order_number, item_id, quantity, price, order_time) VALUES (?, ?, ?, ?, ?)",
                           (orderNumber, order['item_id'], order['item_quantity'], int(order['item_price'].replace(",", "")), order['order_time']))
                db.connection.commit()
            else:
                db.execute("INSERT INTO orderitems (order_number, item_id, quantity, price, order_time) VALUES (?, ?, ?, ?, datetime('now'))",
                           (orderNumber, order['item_id'], order['item_quantity'], int(order['item_price'].replace(",", ""))))
                db.connection.commit()
class Ev:
    def __init__(self):
        self.clkey = os.getenv("PUBLIC_CLIENT", "")
        self.svkey = os.getenv("SERVER_KEY", "")
        self.ngdomain = os.getenv("NGROK_DOMAIN", "")
        self.ngauth = os.getenv("NGROK_AUTH", "")
        self.db = os.getenv("DATABASE_URL", "")


if gui:
    from PyQt6.QtCore import QUrl, Qt
    from PyQt6.QtGui import QIcon,  QPainter, QPageSize, QPageLayout
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
    from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog
    from PyQt6.QtWebEngineWidgets import QWebEngineView

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl("http://127.0.0.1:5000"))  
            self.setCentralWidget(self.browser)

            self.setWindowTitle("Minipos")
            self.setGeometry(0, 0, 2560, 1600)

        def run_gui():
            app = QApplication(sys.argv)
            screen_size = app.primaryScreen().size()
            app.setWindowIcon(QIcon("icon.ico"))
            width, height = int(screen_size.width() * 0.3), int(screen_size.height() * 0.4)
            window = MainWindow()
            window.resize(width, height)
            window.show()
            sys.exit(app.exec())

    class Printable(QWidget):
        def print_receipt(self):
            """Shows a print preview before printing the receipt."""
            printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)

            # Set A4 page size & orientation
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4Small))
            printer.setPageOrientation(QPageLayout.Orientation.Portrait)

            # Create Print Preview Dialog
            preview_dialog = QPrintPreviewDialog(printer, self)
            preview_dialog.resize(900, 700)  
            preview_dialog.setWindowTitle("Print Preview - Receipt") 
            preview_dialog.paintRequested.connect(lambda p: self.render_receipt(p))
            preview_dialog.exec()  # Show preview

        def render_receipt(self, printer):
            """Handles rendering the receipt to the printer or print preview."""
            painter = QPainter(printer)

            # Get the printable area (adjust for margins)
            page_rect = printer.pageRect(QPrinter.Unit.Millimeter)
            widget_rect = self.findChild(QFrame).rect()  

            # Convert QRect to float values
            page_width = page_rect.width()
            page_height = page_rect.height()
            widget_width = widget_rect.width()
            widget_height = widget_rect.height()

            # Set background to white
            painter.fillRect(printer.pageRect(QPrinter.Unit.Point), Qt.GlobalColor.white)

            # Calculate proper scaling
            scale_x = page_width / widget_width * 2
            scale_y = page_height / widget_height * 2 
            scale = min(scale_x, scale_y)  

            # Apply transformations to center and scale the receipt
            painter.translate(page_width / 2 + 480, page_height / 2 + 700)
            painter.scale(scale, scale)
            painter.translate(-widget_width / 2, -widget_height / 2)

            # Render only the receipt card (not the entire window)
            self.findChild(QFrame).render(painter)

            painter.end()

        
        def printer_window(cls,orders):
            app = QApplication([])
            window = cls(orders)
            window.show()
            app.exec()

    class Receipt(Printable):
        def __init__(self, orders):
            super().__init__()
            
            self.setWindowTitle("Receipt")
            self.setFixedWidth(330)   # Adjusted for print button
            self.adjustSize()

            # ======= Main Layout =======
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(10, 10, 10, 10)

            # ======= Card Frame (Receipt Border) =======
            card = QFrame()
            card.setFrameStyle(QFrame.Shape.NoFrame)
            card.setLineWidth(1)
            card.setStyleSheet("font-family: monospace; background-color: white; color: black;")

            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(10, 10, 10, 10)

            # ======= Header (Cafe Info) =======
            if orders[0]["payment_method"]:
                header = QVBoxLayout()
                title = QLabel("<b>Mini Cafe</b>")
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                address = QLabel("Jl. Kembang Harum XI xy-2\nPhone: 1234567890\nJakarta Barat")
                address.setAlignment(Qt.AlignmentFlag.AlignCenter)
                header.addWidget(title)
                header.addWidget(address)
            else:
                header = QVBoxLayout()
                title = QLabel("<h2>Temporary Invoice</h2>")
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                header.addWidget(title)

            # ======= Order Info =======
            if orders:
                order_number = orders[0]["order_number"]
                invoice_number = orders[0]["invoice_number"]
                total_amount = orders[0]["total_amount"]
                payment_method = orders[0]["payment_method"]
                payment_amount = orders[0]["payment_amount"]
                discount = orders[0]["discount"]
                change =  0 if orders[0]["change"] < 0 else orders[0]["change"]  
            else:
                order_number, invoice_number, total_amount, payment_method, payment_amount, discount, change = ("-", "-", 0, "-", "-", 0, 0)

            order_info = QLabel(f"Order #{order_number}\nInvoice Number: {invoice_number}")
            order_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
            order_info.setStyleSheet("border-bottom: 1px dashed black; padding: 5px 0px; font-size: 11px; border-top: 1px dashed black;")

            # ======= Items List =======
            items_layout = QHBoxLayout()
            left_items = QVBoxLayout()
            right_prices = QVBoxLayout()

            left_items.addWidget(QLabel("<b>Items</b>"))
            right_prices.addWidget(QLabel("<b>Total</b>"))

            for idx, item in enumerate(orders, start=1):
                item_name = item["item_name"]
                price = item["price"]
                quantity = item["quantity"]
                total_price = item["total"]

                left_items.addWidget(QLabel(f"{idx}. {item_name}"))
                left_items.addWidget(QLabel(f"<small>Rp {price:,.0f}/pcs x {quantity}</small>"))

                right_prices.addWidget(QLabel(f"Rp {total_price:,.0f}"))
                right_prices.addWidget(QLabel(""))

            items_layout.addLayout(left_items)
            items_layout.addSpacing(85)
            items_layout.addLayout(right_prices)

            # ======= Summary (Tax, Payment, Grand Total) =======
            summary_layout = QHBoxLayout()

            left_summary = QVBoxLayout()
            right_summary = QVBoxLayout()

            # Assume tax is 10% of total amount
            tax = total_amount * 0.1

            left_summary.addWidget(QLabel("Tax:"))
            left_summary.addWidget(QLabel("Payment method:"))
            left_summary.addWidget(QLabel("Paid amount:"))
            left_summary.addWidget(QLabel("Change:"))
            left_summary.addWidget(QLabel("Discount:"))
            left_summary.addWidget(QLabel("Grand Total:"))

            right_summary.addWidget(QLabel(f"Rp {tax:,.0f}"))
            right_summary.addWidget(QLabel(payment_method))
            right_summary.addWidget(QLabel(f"Rp {payment_amount:,.0f}"))
            right_summary.addWidget(QLabel(f"Rp {change:,.0f}"))
            right_summary.addWidget(QLabel(f"{discount}%"))
            right_summary.addWidget(QLabel(f"Rp {total_amount:,.0f}"))

            summary_layout.addLayout(left_summary)
            summary_layout.addSpacing(120)
            summary_layout.addLayout(right_summary)

            # ======= Thank You Note =======
            footer = QLabel("<small>Thank you, please come again!</small>")
            footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
            footer.setStyleSheet("padding: 5px 0px; font-size: 11px; border-top: 1px dashed black; display:block")

            # ======= Print Button =======
            print_button = QPushButton("Print Receipt")
            print_button.clicked.connect(self.print_receipt)

            # ======= Add Widgets to Card Layout =======
            card_layout.addLayout(header)
            card_layout.addWidget(order_info)
            card_layout.addLayout(items_layout)
            card_layout.addSpacing(20)
            card_layout.addLayout(summary_layout)
            card_layout.addWidget(footer)

            card.setLayout(card_layout)

            # ======= Add Card to Main Layout =======
            main_layout.addWidget(card)
            main_layout.addWidget(print_button, alignment=Qt.AlignmentFlag.AlignCenter)
            self.setLayout(main_layout)

    class Ticket(Printable):
        def __init__(self, orders):
            super().__init__()
            
            self.setWindowTitle("Order Summary")
            self.setFixedWidth(330)   
            self.adjustSize()    
        
             # ======= Main Layout =======
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(10, 10, 10, 10)

            # ======= Card Frame (Receipt Border) =======
            card = QFrame()
            card.setFrameStyle(QFrame.Shape.NoFrame)
            card.setLineWidth(1)
            card.setStyleSheet("font-family: monospace; background-color: white; color: black;")

            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(10, 10, 10, 10)

            # ======= Header (Cafe Info) =======
            header = QVBoxLayout()
            title = QLabel("<h2>Order Summary</h2>")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("border-bottom:1px dashed black; padding: 5px;")
            header.addWidget(title)

            # ======= Items List =======
            items_layout = QHBoxLayout()
            left_items = QVBoxLayout()
            
            left_items.addWidget(QLabel("<b>Items</b>"))

            for idx, item in enumerate(orders, start=1):
                item_name = item["item_name"]
                
                quantity = item["quantity"]
                
                left_items.addWidget(QLabel(f"{idx}. {item_name} x {quantity}"))

            items_layout.addLayout(left_items)
            # ======= Print Button =======
            print_button = QPushButton("Print Order")
            print_button.clicked.connect(self.print_receipt)

            # ======= Add Widgets to Card Layout =======
            card_layout.addLayout(header)
            card_layout.addLayout(items_layout)
            card.setLayout(card_layout)

            # ======= Add Card to Main Layout =======
            main_layout.addWidget(card)
            main_layout.addWidget(print_button, alignment=Qt.AlignmentFlag.AlignCenter)
            self.setLayout(main_layout)
    
class Emailer:
    def __init__(self, receiver_email):
        self.sender_email = "minipos.tech@gmail.com"
        self.sender_password = os.getenv("APP_PASS", "")
        self.receiver_email = receiver_email
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, subject, body):
        # Create message
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # Send email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}")
    
    def send_registration_email(self, user_name):
        subject = "🎉Welcome to Minipos - Registration Successful!"
        body = f"""
        <html>
            <body>
                <div class="container">
                    <h2>Welcome to Minipos, {user_name}! </h2>
                    <p>We're excited to welcome you to Minipos! Your email <b>({self.receiver_email})</b> has been successfully registered.</p>
                    <p>You can now log in and start exploring our features. If you didn't register for this account, please ignore this email.</p>
                    <p>If you have any questions, feel free to contact us at <a href="mailto:minipos.tech@gmail.com">minipos.tech@gmail.com</a>.</p>
                    <p class="footer">Best regards,<br><b>The Minipos Team</b></p>
                </div>
            </body>
        </html>
        """
        self.send_email(subject, body)
    
    def send_password_reset(self, user_name, reset_link):
        subject = "🔒Password Reset Request - Minipos"
        body = f"""
        <html>
            <body>
                <div class="container">
                    <p class="header">Password Reset Request</p>
                    <p>Hello { user_name },</p>
                    <p>We received a request to reset your password for your account ({self.receiver_email}).</p>
                    <p>If you didn't request this, you can ignore this email.</p>
                    <p>To reset your password, click the button below:</p>
                    <p><a class="btn" href="{ reset_link }">Reset Password</a></p>
                    <p>If the button doesn’t work, copy and paste this link into your browser:</p>
                    <p>{ reset_link }</p>
                    <div class="footer">Best regards, <br> The Minipos Team</div>
                </div>
            </body>
        </html>
        """
        self.send_email(subject, body)

    def save_expiration_token(id, token, expiration):
        # Save the expiration token to the database 
        db.execute("INSERT INTO password_reset (business_id, token, expiration) VALUES (?, ?, ?)", (id, token, expiration))
        db.connection.commit()
    
    def search_token(token):
        # Search for the token in the database
        return db.execute("SELECT token FROM password_reset WHERE token = ? AND expiration > datetime('now')",  (token, ))
        