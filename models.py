from conn import SQL
import os
from helpers import apology, login_required, thankYou, parseInt, formatCurrency, bankTransfer, generate_order_number, clear_session, generate_random_string, createImageUrl
from dotenv import load_dotenv

load_dotenv()
db = SQL(os.getenv('DATABASE_URL'))

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
    
class Checkout:
    def get_active_discount_ticket():
        return db.execute(
        "SELECT * FROM discount_ticket WHERE expiration_date > datetime('now')").fetchall()

class Users:
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
            param = bankTransfer(orderNumber, total)
            charge_response = core.charge(param)
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