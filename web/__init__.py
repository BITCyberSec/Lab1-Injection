from flask import Flask
import re
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/kontakt')
    def kontakt():
        return render_template('kontakt.html')

    @app.route('/cennik')
    def cennik():
        return render_template('cennik.html')

    @app.route('/szukaj')
    def szukaj():
        return 'Hello World!'

    @app.route('/auth')
    def auth():
        return render_template('zaloguj.html')

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

    app.register_blueprint(admin)
    from . import db
    db.init_app(app)

    # print(app.url_map)
    return app
