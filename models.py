from conn import SQL
import os
from helpers import apology, login_required, thankYou, parseInt, formatCurrency, bankTransfer, generate_order_number, clear_session, generate_random_string, createImageUrl
from dotenv import load_dotenv
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys

load_dotenv()
db = SQL(os.getenv('DATABASE_URL'))

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
                        (orderNumber, deliveryType, tableNumber, "new", int(total.replace(",", "")), discount,)).fetchone()
        
        # Fetch the returned order number and order_date
        order_number, order_date = result

        # save order items to database
        for order in orders:
            db.execute("INSERT INTO orderitems (order_number, item_id, quantity, price, order_time) VALUES (?, ?, ?, ?, ?)",
                    (order_number, order['item_id'], order['item_quantity'], int(order['item_price'].replace(",", "")), order_date))
        

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
            param = bankTransfer(orderNumber, total)
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
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:5000"))  # Wrap the URL with QUrl
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