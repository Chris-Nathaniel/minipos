# Standard Library Imports
import os
import sys
import time
import secrets
import subprocess
import threading
import re
import string
import ctypes
import random
import urllib.parse
import datetime
import logging
from datetime import date
from functools import wraps 
import multiprocessing

# Third-Party Imports
from flask import Flask, render_template, request, session, redirect, flash, jsonify, current_app, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import requests
import sqlite3
from urllib.parse import urlparse
import midtransclient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ngrok

# custom Imports
from helpers_module.dbinit import *

# PyQt6 Imports
def check_gui():
    try:
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QIcon, QTextDocument
        from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
        from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        return True
    except Exception as e:
        print(f"GUI import failed: {e}")
        return False

gui = check_gui()


