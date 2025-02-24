# Minipos
#### Video Demo:

## Description
Minipos is a standalone simple Point of Sale (POS) system designed for small cafes and restaurants. This project was developed as my final submission for CS50x - Introduction to Computer Science. The goal of Minipos is to provide an easy-to-use, lightweight, and functional POS system that helps small business owners manage orders, track sales, and streamline their daily operations.
The app was developed using VisualStudio Code and was completed in Jakarta, Indonesia.

## Designs
There are three things my app requires, my app runs on a single machine and doesn't require constant public access, Easy installation the user should not know write any code to run my app, dealing with dependencies and envs, Lastly a public url for integrations. With that in my i came up with these solution, batch script to help me run my python app from the desktop and help me with managing dependencies. This may not be the best approach of installing a standalone application but this is the solution that i had came up with at that time and most familiar with it. Ngrok provided me with a static public url that helps me expose my local app to the public for a limited time period untill my app closes.

This app are built with a one user and one database in mind which means that only one user can registered to the app. I was debating whether pre registering an account or put a mock data inside or make a completely empty database submission However in this cs50 codespace for this demo i have created a pre-made database to help run the app without having to run installation.bat files.

## Getting Started - Installation
1. Download the app to your local file
2. Run installation.bat > a shortcut to minipos.exe should be created on your desktop
3. Run minipos.exe

there are a few things that installation.bat does:
~install python3.11
~install sqlite3
~install all dependencies from requirements.txt
~set up env and sqlite3 database tables.

## compatibality
Since Minipos are built on windows operating system, i made it only with windows compatibility, thus any functionality that .bat files use may not work well in other operating system.

- Windows - fully-compatible.
- Mac- semi-compatible. (manually install dependencies, reset/create new database wont work, .bat files not working)

## interface
The program can be run on windowed gui mode or on browser making it very flexible choice.

## Features
- Menu system
- Cart system
- Order tracking
- Discount vouchers
- Menu customization
- Order management
- Midtrans integration
- SMTP email support

## Source Files

__init__.py manage imports

app.py - Main app file containing the routes to all other html pages

conn.py - Connecting to database, port forwarding with ngrok, connecting to midtrans

Models.py - classes and database queries along with gui

Helpers.py - contains functions

## Design

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
