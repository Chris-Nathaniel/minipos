# Minipos
#### Video Demo: https://www.youtube.com/watch?v=HQXEEZAdVIA

## Description

Minipos is a simple yet efficient Point of Sale (POS) system designed for small cafes and restaurants. This project was developed as my final submission for CS50x - Introduction to Computer Science. The goal of Minipos is to provide an easy-to-use, lightweight, and functional POS system that helps small business owners manage orders, track sales, and streamline their daily operations. Features: Menu System, Cart System, Discount system, Order Tracking system, Payment Gateway.

The app was developed using VisualStudio Code and was completed in Jakarta, Indonesia.

The project is built in Python using the Flask framework for my back-end. I used Javascript, Html and CSS using Bootstrap to streamlined the front-end. I chosed to use sqlite3 for my project due to its simplicity and portability.

## Source Files
app.py - Main app file containing the routes to all other html pages

conn.py - Connecting to database

Models.py - classes and database queries

forms.py - All WTForms Form objects for app

## Technology
Flask - I used Flask as my primary web framework as it is one i am familiar with, including in Week 8 Homepage  of CS50. It is easy to use, and the app is simple enough that it doesn't require performance benefits that might have been provided by other frameworks.

SQLite3 – I chose SQLite3 as the database for this project because it is lightweight, requires minimal setup, and is well-suited for small to medium-sized applications like this one. Since Flask comes with built-in support for SQLite, it integrates seamlessly without needing a separate database server. Additionally, SQLite stores data in a single file, making it easy to manage and deploy.

Bootstrap - I am using Bootstrap 5 for my front-end framework. It provides a fairly easy to use toolset to quickly provide high-quality, professional looking design.

## Hosting
This project is designed to run locally, so it is not hosted on any cloud platform. Since SQLite3 is a file-based database, it does not require a separate database server, making local development and testing straightforward. Flask's built-in development server is sufficient for running the app during development.

I was able to get the app working seamlessly using .bat file, I have also tried setting up a port forwarding using ngrok so that any notifications from the payment gateway can be directly received back to the ngrok address.

## Inspiration
My family had the idea of opening a small cafe and thats where i got my inspiration of making a small POS system.
