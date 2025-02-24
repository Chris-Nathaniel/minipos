# Minipos
#### Video Demo:

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
- password: 1234

## Getting Started - Installation
1. Download the app to your local file
2. Run installation.bat > a shortcut to minipos.exe should be created on your desktop
3. Run minipos.exe

there are a few things that installation.bat does:
- install python3.11
- install sqlite3
- install all dependencies from requirements.txt
- set up env and sqlite3 database tables.

## compatibality
Since Minipos was developed for Windows, it is fully compatible with that operating system. Some functionality (such as .bat and .exe files) may not work properly on other operating systems.

- Windows - fully-compatible.
- Mac – Semi-compatible (Users must manually install dependencies; .bat and .exe files will not work, and the app must be started manually.)

## interface
The program can run in windowed GUI mode or via a web browser, making it a flexible choice for different usage scenarios.

## Features
- Menu system - Allows users to create Orders
- Cart system - Enables easy order selection before finalizing transactions.
- Order tracking - Keeps a record of past orders for easy reference.
- Discount vouchers - Provides the ability to apply promotional discounts.
- Menu customization - Allows full control over menu pricing
- Order management- Facilitates modifying or canceling orders as needed.
- Midtrans integration - Automate online banking transaction validation.
- SMTP email support - Enables email receipts and notifications.

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