import re
from web import app
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/kontakt')
def kontakt():
    return 'Hello World!'


@app.route('/cennik')
def cennik():
    return 'Hello World!'


@app.route('/szukaj')
def szukaj():
    return 'Hello World!'


@app.route('/auth')
def auth():
    return 'Hello World!'


@app.route('/auto')
def auto():
    return 'Hello World!'


@app.route('/wypozycz')
def wypozycz():
    return 'Hello World!'


admin = Blueprint('admin',
                  __name__,
                  url_prefix='/admin',
                  template_folder='templates')

@admin.route('/update')
def admin_view():
    return "aaaa"

@admin.route('/add_user')
def add_user():
    return "bbb"