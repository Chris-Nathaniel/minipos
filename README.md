# Minipos
#### Video Demo: https://youtu.be/a2nO6ZCf9Ao

## Description
Minipos is a standalone, simple Point of Sale (POS) system designed for small cafes and restaurants. This project was developed as my final submission for CS50x - Introduction to Computer Science. The goal of Minipos is to provide an easy-to-use, lightweight, and functional POS system that helps small business owners manage orders, track sales, and streamline their daily operations.

The app was developed using Visual Studio Code and was completed in Jakarta, Indonesia.

## Designs
There are three key aspects I considered while designing Minipos:

- Local Operation – The app runs on a single machine and does not require constant public access.
- Easy Installation – Users should not need to write any code, manage dependencies, or set up environments manually.
- Public URL for Integrations – The system should allow limited external access when needed.

To address these requirements, I created a batch script to help users run the Python app from their desktop while managing dependencies. While this may not be the best approach for installing a standalone application, it was the most practical solution I was familiar with at the time. Additionally, I used Ngrok to provide a temporary static public URL, allowing limited external access until the app is closed.

This app is designed with a single user and a single database in mind, meaning only one user can be registered. For this CS50 project, I have created a pre-registered account with mock data:

- username: admin
- password: thisiscs50

## Getting Started - Installation
1. Download the app to your local file
2. Run installation.bat > a shortcut to minipos.exe should be created on your desktop
3. Run minipos.exe

there are a few things that installation.bat does:
- install python3.11
- install sqlite3
- install all dependencies from requirements.txt
- set up env and sqlite3 database tables.

## Compatibality
Since Minipos was developed for Windows, it is fully compatible with that operating system. Some functionality (such as .bat and .exe files) may not work properly on other operating systems.

- Windows - fully-compatible.
- Mac – Semi-compatible (Users must manually install dependencies; .bat and .exe files will not work, and the app must be started manually.)

## interface
The program can run in windowed GUI mode or via a web browser, making it a flexible choice for different usage scenarios.

## App Features
1) Menu and Cart system- Allows users to create Orders, enables easy order selection before finalizing transactions.
![alt text](/static/images/Menu.png)
The first page I built for Minipos was the menu and cart system, which included layout.html, category.html, menu.html, and billing.html. One of the challenges I faced while developing the cart system was preventing the page from refreshing whenever an item was added to the cart. To solve this, I learned how to send and receive data between the front end and back end using JavaScript’s fetch function along with the .then() method. This allowed for a smoother user experience by updating the cart dynamically without requiring a full page reload.

The menu data is taken from the menu_list table in the database, and each item added to the cart is stored in a "cart" session variable. The cart data is then processed to calculate the total, total quantity, tax, and discount, which are displayed in the billing section. The tax that are used in this app assumes 10% VAT. although indonesian policy had changed this into 11%, for convenience purposes i'll stick with 10%. although in the future i might have changed this into a more configurable.

2) Order and payment tracking - Keeps a record of past orders for easy reference, Keep track of orders payment status.
![alt text](/static/images/Orders.png)
![alt text](/static/images/action.png)
Designing the orders table is one i am proud of. I wanted a table design that doesn't take a lot of space, mobile user friendly and has a lot of functionality.
- edit and cancel orders
there are certain limitations i implement here to ensure security, you cannot cancel and edit orders that where status is paid or pending. i have also added different time for new orders that got added later on. Although it is not being displayed anywhere on the current state of the project, it is stored on the orderitems database. I think this will be a good method in the future to tell the kitchen how long ago the orders was made.

- show clear status indicators of the payment status
the payment status are divided into 4 mainly 4 status: unpaid, pending, paid and failed. 

- Orders are categorized into Dine-in, Takeout, Completed, and Cancelled, allowing easy navigation between different order types.
I structured the order flow this way to eliminate confusion about order status. New orders are automatically placed under Dine-in or Takeout, based on the customer’s selection.
Order completion is handled manually via a button instead of being automatically marked as completed. This provides flexibility in determining when an order is considered complete.
Some businesses may consider an order complete once payment is received. Others may prefer to keep the order active until all food has been served.

- Print/View Receipts
I implemented two printing methods: QPrinter and the browser's built-in print function. The system determines which method to use based on the request header whether the input comes from a web browser or the application’s GUI. While QPrinter works for both the browser and the GUI, I initially developed the app for the web, making it hard for me to let go of the browser-based printing method.
If a receipt is printed before the customer has paid, the system generates a temporary invoice instead of a final receipt. This ensures that customers receive a bill for reference without it being mistaken for a proof of payment. Once the payment is completed, a proper receipt can be printed.

- Database: orders
The orders data here are split into two tables, orders and orderitems. The orders table stores the order info as a whole like order number, table number, total, order types, order status and date. while the orderitems stores the individual items associated with each order, such as the specific dishes or drinks ordered. 

3) Discount vouchers - Provides the ability to apply promotional discounts.
![alt text](/static/images/Discount.png)
I implemented a simple discount system that allows users to apply and remove discount codes from their orders. One of the toughest challenges was ensuring that the total bill was displayed correctly, especially when users added or removed items after applying a discount.

How Discounts Are Calculated:
The discount is percentage-based (e.g., 10% off).
Since tax is not discounted, it is always calculated on the original subtotal before applying the discount.

- Menu customization - Allows full control over menu pricing, description, name, category and images.
![alt text](/static/images/Customization.png)
- change menu item details (name, pictures, description, price )
- bulk delete
- add new item
- add category

- Midtrans integration - Automate online banking transaction validation.
![alt text](/static/images/midtransinter.png)
- This is the first time i have tried integrating with payment gateway with my own project, there was this one problem i had when integrating with midtrans, midtrans only allows unique
order number. Although this is good in some ways to prevent any double entry, however if we wanted to apply a shorter payment expiry, or say in a situation where one accidentally cancel the payment method, or even debugging where one user has to reset the database over and over. this prevent the app from choosing the same payment method for that order number. 
My first approach was to add a prefix to the order number, thinking I could later modify it when moving to production. While this helped with database resets, it still didn't allow me to resubmit the same order number. 
Next, I considered appending a timestamp to the order number before sending it to Midtrans while keeping the original order number (with a suffix) in my database. This allowed me to differentiate payments without cluttering my order table.
However, this method had a downside: if Midtrans' payment notification failed to reach my app, I couldn't check the payment status without knowing the exact time the order was submitted. This highlighted a flaw—not storing the formatted order number in the database made tracking payments unreliable.
The final solution, which I ultimately adopted, was similar to the second but improved upon it. Instead of relying solely on datetime formatting, I introduced a count table to track how many times an order number was submitted. I then tokenized the database and combined the count value to generate a unique order name for each attempt and for each database instance.

- SMTP email support - Email based password resets.

## Source Files

__init__.py Manages imports and application setup.

app.py - The main app file containing all route definitions.

conn.py - Handles database connections, port forwarding with Ngrok, and Midtrans payment gateway integration.

Models.py - Defines classes and database queries for the application.

Helpers.py - Contains utility functions to support the main app.

dbgenerator.py - Helps in rebuilding and resetting database tables when needed.

## Technology
Minipos is built using Python with the Flask framework for the backend. The frontend is built using HTML, CSS, and JavaScript with Bootstrap for styling. SQLite3 is used as the database due to its simplicity and portability.

Frameworks & Libraries
- Flask – Chosen for its ease of use and familiarity (as introduced in Week 9: Finance of CS50). The app is simple enough that it does not require a more complex framework.

- SQLite3 – A lightweight, self-contained database, ideal for small to medium-sized applications. Since Flask has built-in support for SQLite, integration is seamless. SQLite stores data in a single file, making it easy to manage and deploy.
- Bootstrap 5 – Used for the frontend to provide a clean, professional-looking design with minimal effort.

## Hosting
This project is designed to run locally, so it is not hosted on any cloud platform. Since SQLite3 is a file-based database, it does not require a separate database server, making local development and testing straightforward. Flask's built-in development server is sufficient for running the app during development.

## Inspiration
I have always wanted to open a small cafe, and that inspired me to create a simple POS system made for such businesses. The idea was to build something that I, or someone in a similar position, could actually use without needing an expensive or complex system. Developing this project for CS50x gave me the opportunity to turn that idea into a working application.

## what can be improve on?
My app has a lot of potential for future enhancements. Some key improvements I have in mind include:
More configurable tax settings to allow flexibility based on different tax rules.
Role-based access control, so only authorized users can configure settings or customize the menu.
Generating reports for daily and monthly sales to help with business insights.
Exporting order data to Excel for better record-keeping and analysis.