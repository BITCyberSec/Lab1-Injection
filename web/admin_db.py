import sqlite3
from sqlite3.dbapi2 import Error
import click
import random
import string
from termcolor import colored
from flask import current_app, g, url_for
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_ADMIN'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('admin_schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    auta = [
        ('Mercedes C63S', "1.2l", "Gaz",
         "automatyczna", 5, "images/auta/merc.jpg"),
        ('Ford Fiesta', "2l", "Benzyna", "manualna", 5, "images/auta/fiesta.jpg"),
        ('Opel Astra', "1.6l", "Diesel", "manualna", 5, "images/auta/astra.jpg"),
        ('Honda Civic', "1.8l", "Benzyna", "manualna", 5, "images/auta/civic.jpg")
    ]
    for val in auta:
        try:
            print(val)      
            db.execute(
                "INSERT INTO auta (car_name, engine, fuel, gearbox, seats, car_image) VALUES (?, ?, ?, ?, ?, ?)", val)
            db.commit()
        except Error as e:
            print(colored(e, "red"))
    try:
        db.execute(
            "INSERT INTO user (username, passwd) VALUES (?, ?)",
            (''.join(random.choice(string.ascii_letters) for i in range(20)),
            ''.join(random.choice(string.ascii_letters) for i in range(20))))
        db.commit()
    except Error as e:
        print(colored(e, "red"))

@click.command('init-admin-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized admin database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
