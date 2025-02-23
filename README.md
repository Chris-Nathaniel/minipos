# Minipos
#### Video Demo: https://www.youtube.com/watch?v=HQXEEZAdVIA

## Description
Minipos is a simple Point of Sale (POS) system designed for small cafes and restaurants. This project was developed as my final submission for CS50x - Introduction to Computer Science. The goal of Minipos is to provide an easy-to-use, lightweight, and functional POS system that helps small business owners manage orders, track sales, and streamline their daily operations.
The app was developed using VisualStudio Code and was completed in Jakarta, Indonesia.

## Getting Started - Installation
i wanted to make an app that feels like an app. meaning that i wanted my program to run locally and easy to set up and install, the user should not know write any code to run my app with. With that in my i came up with a solution to use batch script to help me run my python app from the desktop and help with the installation process. I got this inpiration while i was trying to learn how to use stable diffusion web ui and finally came up with this. Since Minipos are built on windows operating system, i made it only with windows compatibility, thus .bat files are not supported
any other operating system. However in this cs50 codespace for this demo i have created a pre-made database to help run the app without having to run installation.bat files.

>>Installtion process
1. Download the app to your local file
2. Run installation.bat > a shortcut to minipos.exe should be created on your desktop
3. Run minipos.exe

there are a few things that installation.bat does:
~install python3.11
~install sqlite3
~install all dependencies from requirements.txt
~set up env and sqlite3 database tables.

## compatibality
Windows - fully-compatible.
Mac- semi-compatible. (manually install dependencies, reset/create new database wont work.)

## interface
The program can be run on windowed gui mode or on browser making it very flexible choice.

## Features
Menu system
Cart system
Order tracking
Discount vouchers
Menu customization
Order management
Midtrans integration
SMTP email support

## Source Files

__init__.py manage imports

app.py - Main app file containing the routes to all other html pages

conn.py - Connecting to database, port forwarding with ngrok, connecting to midtrans

Models.py - classes and database queries along with gui

Helpers.py - contains functions

## Technology
Minipos is built with Python using the Flask framework for my back-end. I used Javascript, Html and CSS using Bootstrap to streamlined the front-end. I chosed to use sqlite3 for my project due to its simplicity and portability.

Flask - I used Flask as my primary web framework as it is one i am familiar with, including in Week 9 Finance of CS50. It is easy to use, and the app is simple enough that it doesn't require performance benefits that might have been provided by other frameworks.

SQLite3 – I chose SQLite3 as the database for this project because it is lightweight, requires minimal setup, and is well-suited for small to medium-sized applications like this one. Since Flask comes with built-in support for SQLite, it integrates seamlessly without needing a separate database server. Additionally, SQLite stores data in a single file, making it easy to manage and deploy.

Bootstrap - I am using Bootstrap 5 for my front-end framework. It provides a fairly easy to use toolset to quickly provide high-quality, professional looking design.

## Hosting
This project is designed to run locally, so it is not hosted on any cloud platform. Since SQLite3 is a file-based database, it does not require a separate database server, making local development and testing straightforward. Flask's built-in development server is sufficient for running the app during development.

I was able to get the app working seamlessly using .bat file, I have also tried setting up a port forwarding using ngrok so that any notifications from the payment gateway can be directly received back to the ngrok address.

## Inspiration
I had wanted to open a small cafe and thats where i got my inspiration of making a small POS system.
