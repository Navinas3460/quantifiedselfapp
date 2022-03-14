from string import ascii_lowercase, ascii_uppercase
from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory
from flask_bcrypt import Bcrypt
from models import *
from datetime import datetime
from os import path

app = Flask(__name__, template_folder="../templates", static_url_path='', static_folder="../static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../quantifiedselfapp.sqlite3'
app.secret_key = "myapp123"

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user_login"


app.app_context().push()
logged_in_as = ""

from app import userviews
from app import trackerviews
from app import logviews