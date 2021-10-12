from flask import Flask
import re
from flask import (
    Blueprint,
    render_template,
    abort,
    flash,
    g,
    redirect,
    request,
    session,
    url_for,
)
from jinja2 import TemplateNotFound
import functools
from werkzeug.security import check_password_hash, generate_password_hash

from web.user_db import get_db as get_user_db
from web.admin_db import get_db as get_admin_db


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/kontakt")
    def kontakt():
        return render_template("kontakt.html")

    @app.route("/cennik")
    def cennik():
        return render_template("cennik.html")

    @app.route("/szukaj")
    def szukaj():
        return "Hello World!"

    @app.route("/auth", methods=["GET", "POST"])
    def auth():
        if request.method == "GET":
            return render_template("zaloguj.html")
        elif request.method == "POST":
            if_register = True if request.form["login"] == "register" else False
            if if_register:
                first_name = request.form["first_name"]
                surname = request.form["surname"]
                email = request.form["email"]
                phone = request.form["phone"]
                password = request.form["passwd"]
                password_repeat = request.form["passwd_repeat"]
                error = None
                if not all(
                    [first_name, surname, email, phone, password, password_repeat]
                ):
                    error = "Not all fields have value"
                elif not re.match(r"^\w{1,30}$", first_name):
                    error = "Invalid first name"
                elif not re.match(r"^\w{1,30}$", surname):
                    error = "Invalid surname"
                elif not re.match(
                    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email
                ):
                    error = "Invalid email"
                elif not re.match(r"^[\+\(]?\d+(?:[- \)\(]+\d+)+$", phone):
                    error = "Invalid phone number"
                elif password != password_repeat:
                    error = "Passwords do not match"

                if error is None:
                    pass
                    # TODO: Add sql statements

                return render_template("zaloguj.html", error=error)

            else:
                sql_restricted = ["OR", "AND", "SELECT"]
                username = request.form["username"]
                password = request.form["password"]
                error = None

                if not username:
                    error = "Empty username"
                elif not password:
                    error = "Empty password"
                elif any(
                    word in (username + password).upper() for word in sql_restricted
                ):
                    error = "Invalid username or password"

                user_db = get_user_db()
                user_data = user_db.execute(
                    f"SELECT * FROM user WHERE username = '{username}'"
                ).fetchone()

                if user_data is None:
                    error = "Wrong username or password!"
                elif user_data["passwd"] != password:
                    error = "Wrong username or password!"

                if error is None:
                    return redirect("/")
                    # TODO: Add session itp
                return render_template("zaloguj.html", error=error)

    @app.route("/auto")
    def auto():
        return "Hello World!"

    @app.route("/wypozycz")
    def wypozycz():
        return "Hello World!"

    admin = Blueprint(
        "admin", __name__, url_prefix="/admin", template_folder="templates"
    )

    @admin.route("/update")
    def admin_view():
        return "aaaa"

    @admin.route("/add_user")
    def add_user():
        return "bbb"

    app.register_blueprint(admin)
    from . import user_db

    user_db.init_app(app)
    from . import admin_db

    admin_db.init_app(app)
    return app
