from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from FDataBase import FDataBase
from flask_login import LoginManager, login_user, login_required
from UserLogin import UserLogin
import logging
import typer
from functools import cache
import config


DATABASE = "tmp/fldb.db"
DEBUG = "True"
SECRET_KEY = "lkjhgfdsapoiuytrewqer"


logger = logging.getLogger('gunicorn.error')


app = Flask(__name__)
# login_manager.login_view = 'login'
app.config.from_object(__name__)
# app.config.update(dict(DATABASE=os.path.join(app.root_path, 'fldb.db')))
login_manager = LoginManager(app)


@cache
def conn():
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = conn()
    logger.info("start creating db")
    logger.info(f"photos dir is {config.PHOTOS_DIR}")
    with app.open_resource("sq_db.sql", mode="r") as f:
        db.cursor().executescript(f.read())

    for filename in os.listdir(config.PHOTOS_DIR):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
            name = os.path.splitext(filename)[0]
            image_file = "/static/images/{}".format(filename.replace('\\', '/'))
            cursor = db.cursor()
            cursor.execute('SELECT * FROM Images WHERE name = ?', (name,))
            if cursor.fetchone() is None:
                cursor.execute(
                    'INSERT INTO Images (name, image_file) VALUES (?, ?)', (name, image_file))
    db.commit()
    logger.info("db successfully filled with image paths")


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, FDataBase(conn()))


@app.route('/')
# @login_required
def start():
    return render_template('start.html')


@app.route('/category/<int:image_id>', methods=['GET', 'POST'])
def category(image_id):
    c = conn().cursor()
    c.execute("SELECT * FROM Images WHERE id=?", (image_id,))
    image = c.fetchone()
    c.execute("SELECT * FROM Categories")
    categories = c.fetchall()
    if request.method == 'POST':
        category_id = request.form['category']

        c.execute("INSERT INTO Image_Category (image_id, category_id) VALUES (?, ?)",
                  (image_id, category_id))
        conn().commit()

        next_image_id = image_id + 1
        return redirect(url_for('category', image_id=next_image_id))

    return render_template('category.html', image=image, categories=categories)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # session.pop('_flashes', None)
        if len(request.form['name']) > 2 and len(request.form['email']) > 2 \
                and len(request.form['psw']) > 2 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = FDataBase(conn()).addUser(
                request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=FDataBase(conn()).getMenu(), title="Регистрация")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = FDataBase(conn()).getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('index'))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=FDataBase(conn()).getMenu(), title="Авторизация")


@app.route('/aaa')
@login_required
def index():
    c = conn().cursor()
    c.execute("SELECT * FROM Images")
    images = c.fetchall()
    return render_template('index.html', images=images)


cmd_app = typer.Typer()


@cmd_app.command()
def create_database():
    """create sqlite3 db an fill with image paths"""
    create_db()


@cmd_app.command()
def start_app():
    app.run(debug=True, port=5000, host="0.0.0.0")


if __name__ == '__main__':
    cmd_app()
