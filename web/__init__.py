from sqlite3.dbapi2 import Error
from termcolor import colored
from flask import Flask
import re
import os
from jinja2 import contextfilter, Template
from markupsafe import Markup
from flask import (
    Blueprint,
    render_template,
    render_template_string,
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
    # DONE

    @app.route("/")
    def index():
        return render_template("index.html")
    # DONE

    @app.route("/kontakt", methods=["GET", "POST"])
    def kontakt():
        if request.method == "GET":
            return render_template("kontakt.html")
        else:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            message = request.form['message']
            print(message)
            try:
                print(
                    colored(f"echo {message} | sendmail -f {email} -t aaa@aaa.com", "yellow"))
                result = os.system(
                    f"echo {message} | sendmail -f {email} -t aaa@aaa.com")
                if result == 0:
                    return render_template("kontakt.html", message="But how to read output of a comand? :D")
                else:
                    return render_template("kontakt.html", message="Message sent successfuly")
            except Error as e:
                print(colored(f"Error sending mail: {e}", "red"))
                return render_template("kontakt.html", message="Error sending message")
    # DONE

    @app.route("/cennik")
    def cennik():
        return render_template("cennik.html")
    #DONE
    @app.route("/szukaj")
    def szukaj():
        query = request.args.get("query")

        if not query or query == '':
            return redirect("/")

        admin_db = get_admin_db()
        data = admin_db.execute(
            f'''SELECT id, car_name name, engine, car_image image, seats miejsca
            FROM auta 
            WHERE car_name LIKE ?''',
            ('%'+query+'%',)).fetchall()
        cars_list = []
        for i in data:
            cars_list.append(
                {'id': i['id'],
                 'name': i['name'],
                 'engine': i['engine'],
                 'image': i['image'],
                 'miejsca': i['miejsca']
                })
        return render_template("szukaj.html", cars=cars_list)
    # DONE
    @app.route("/auth", methods=["GET", "POST"])
    def auth():
        if request.method == "GET":
            return render_template("zaloguj.html")
        elif request.method == "POST":
            register_flag = True if request.form["login"] == "register" else False
            # REGISTRATION FORM was submited
            if register_flag:

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
                elif not re.match(r"^\d{9}$", phone):
                    error = "Invalid phone number"
                elif password != password_repeat:
                    error = "Passwords do not match"

                if error is None:
                    user_db = get_user_db()
                    try:
                        user_db.execute("INSERT INTO user (passwd, first_name, surname, email, phone) VALUES (?, ?, ?, ?, ?)", (
                            password, first_name, surname, email, phone),)
                        user_db.commit()
                    except user_db.IntegrityError as e:
                        print(
                            colored(f"Exception in adding new user to the table {e}", "red"))
                        render_template(
                            "zaloguj.html", error="User already exists!")
                return render_template("zaloguj.html", error=error)
            # LOGIN FORM was submited
            else:
                email = request.form["email"]
                password = request.form["password"]
                error = None
                print(
                    colored(f"Email: {email}, password: {password}", "green"))
                if not email:
                    error = "Empty username"
                elif not password:
                    error = "Empty password"

                user_db = get_user_db()
                user_data = user_db.execute(
                    f"SELECT * FROM user WHERE email = '{email}'"
                ).fetchone()

                if user_data is None:
                    print(colored("Db did not return any data", "red"))
                    error = "Wrong username or password!"
                elif user_data["passwd"] != password:
                    error = "Wrong username or password!"

                if error is None:
                    return redirect("/")
                return render_template("zaloguj.html", error=error)


    @contextfilter
    def dangerous_render(context, value):
        return Markup(Template(value).render(context)).render()

    @app.route("/auto/<string:id>")
    def auto(id):
        db = get_admin_db()
        car = db.execute(f'SELECT * FROM auta WHERE id={id}').fetchone()
        if car:
            with open('web/templates/auto.html', 'r') as f:
                string = f.read()
            return render_template_string(string.replace("######", car['fuel']), car=car)
        else:
            return abort(404)

    @app.route("/wypozycz")
    def wypozycz():
        return "Hello World!"

    admin = Blueprint(
        "admin", __name__, url_prefix="/admin", template_folder="templates"
    )

    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('admin.admin_login'))
            return view(**kwargs)
        return wrapped_view

    @admin.before_app_request
    def load_logged_in_user():
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_admin_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()

    
    @admin.route("/update/<int:id>", methods=["GET", "POST"])
    @login_required
    def admin_view(id):
        db = get_admin_db()
        if request.method=="GET":
            car = db.execute("SELECT * FROM auta WHERE id=?", (id,)).fetchone()
            if not car:
                return abort(404)
            return render_template("update.html", car=car)
        else:
            car_name = request.form['car_name']
            engine = request.form['engine']
            fuel = request.form['fuel']
            gearbox = request.form['gearbox']
            seats = request.form['seats']
            error = None
            if not all([car_name, engine, fuel, gearbox, seats]):
                error= "All fields must be specified"
            
            if error is None:
                try:
                    db.execute('''
                    UPDATE auta
                    SET car_name = ?,
                    engine = ?,
                    fuel = ?,
                    gearbox = ?,
                    seats = ?
                    WHERE id = ?
                    ''', (car_name, engine, fuel, gearbox, seats, id))
                    db.commit()
                except Error as e:
                    print(colored(f"Error updating db: {e}", "red"))
                return redirect(f'/admin/update/{id}')

    @admin.route("/auth", methods=["GET", "POST"])
    def admin_login():
        if request.method == "GET":
            print("I'm in GET")
            return render_template("admin_auth.html")
        else:
            print("I'm in POST")
            username = request.form['username']
            password = request.form['password']
            error = None
            if not username or not password:
                print("username || psswd == ''")
                print("u:", username)
                print("p: ", password)
                error="Empty username or password"

            if error is None:
                print("error is none")
                admin_db = get_admin_db()   
                a = admin_db.execute(
                    "SELECT username, passwd FROM user").fetchone()
                print("This should be user: ", a['username'], a['passwd'])
                user = admin_db.execute("SELECT * FROM user WHERE username=? AND passwd=?", (username, password)).fetchone()
                print(user)
                if not user:
                    return redirect(url_for("admin.admin_login"))
                session.clear()
                session['user_id'] = user['id']
                return redirect('/admin/update/1')
            return render_template("admin_auth.html", error=error)

    app.register_blueprint(admin)
    from . import user_db

    user_db.init_app(app)
    from . import admin_db

    admin_db.init_app(app)
    return app
