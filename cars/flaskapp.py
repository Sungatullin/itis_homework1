import datetime
import os
import sqlite3

from flask import Flask, render_template, url_for, session, redirect, request, abort, g, flash
from cars.cars_database import FlaskDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from cars.helpers import check_password, check_email
from cars.user_login import UserLogin

DATABASE = 'users.db'
DEBUG = True
SECRET_KEY = 'vbshbvhksbkvskjvk322'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flaskapp.db')))
app.permanent_session_lifetime = datetime.timedelta(days=1)

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().from_fdb(user_id, fdb)


@app.before_first_request
def before_first_request_func():
    print('BEFORE_FIRST REQUEST called!')


fdb = None


@app.before_request
def before_request_func():
    global fdb
    fdb = FlaskDataBase(get_db())
    print('BEFORE REQUEST called!')


@app.after_request
def after_request_func(response):
    print('AFTER REQUEST called!')
    return response


@app.teardown_request
def teardown_request_func(response):
    print('TEARDOWN REQUEST called!')
    return response


def create_db():
    db = connect_db()
    with app.open_resource('carsdb.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route('/')
def index():
    return render_template(
        'index.html',
        menu=fdb.get_menu(),
        title=""
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "logout")
    return redirect(url_for('login'))


@app.route("/profile")
@login_required
def profile():
    if current_user.is_authenticated:
        return render_template(
            'profile.html',
            title='profile',
            menu=fdb.get_menu()
        )
    else:
        return render_template(
            'login.html',
            menu=fdb.get_menu(),
            title='Авторизация'
        )


@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        'page.html',
        title='Ошибка',
        menu=fdb.get_menu(),
        error_text='Страница не найдена'
    )


@app.errorhandler(401)
def page_is_not_authenticated(error):
    return render_template(
        'page.html',
        title='Ошибка',
        menu=fdb.get_menu(),
        error_text='Вы не авторизованы'
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = fdb.get_user_by_email(request.form['email'])
        print(user)
        if not request.form['email']:
            flash("Email не указан", "error")
        elif not request.form['psw']:
            flash("Пароль не указан", "error")
        elif not user:
            flash("Неверный логин", "error")
        elif not check_password_hash(user['psw'], request.form['psw']):
            flash("Неверный пароль", "error")
        else:
            userlogin = UserLogin().create(user)
            if request.form.get('remainme'):
                rm = True
            else:
                rm = False
            login_user(userlogin, remember=rm)
            return redirect(
                url_for("profile")
            )

    return render_template(
        'login.html',
        menu=fdb.get_menu(),
        title='Авторизация'
    )


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if not request.form['name']:
            flash("Имя пользователя не указано", "error")
        elif len(request.form['name']) < 4:
            flash("Имя пользователя должно превышать 4 смиволов", "error")
        elif not request.form['email']:
            flash("Email не указан", "error")
        elif not check_email(request.form['email']):
            flash("Неверный email", "error")
        elif not request.form['psw']:
            flash("Пароль не указан", "error")
        elif not check_password(request.form['psw']):
            flash("Пароль должен превышать 4 символов и должен содержать цифры и буквы латинского алфавита", "error")
        elif not request.form['psw2']:
            flash("Повторный пароль не указан", "error")
        elif not request.form['psw'] == request.form['psw2']:
            flash("Пароли не совпадают", "error")
        else:
            hash = generate_password_hash(request.form['psw'])
            res = fdb.add_user(request.form['name'], request.form['email'], hash)
            if res[0]:
                flash(res[1], "success")
                return redirect(url_for('login'))
            else:
                flash(res[1], "error")
    return render_template(
        'register.html',
        menu=fdb.get_menu(),
        title='Регистрация'
    )


if __name__ == '__main__':
    app.run(debug=True)
