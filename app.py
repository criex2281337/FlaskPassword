from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
import string
import os

app = Flask(__name__)
app.secret_key = 'secret'

DB_FILE = 'users.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            website TEXT NOT NULL,
            login TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()

init_db()


def get_user(username):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, password FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

def save_user(username, password):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()

def save_password(username, website, login, password):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO passwords (username, website, login, password) VALUES (?, ?, ?, ?)',
                       (username, website, login, password))
        conn.commit()

def load_passwords_for_user(username):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT website, login, password FROM passwords WHERE username = ?', (username,))
        return cursor.fetchall()


def generate_password(length, complexity):
    if complexity == 'simple':
        chars = string.ascii_letters + string.digits
    elif complexity == 'medium':
        chars = string.ascii_letters + string.digits + "!@#$%"
    else:
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user[1] == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверный логин или пароль")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return render_template('register.html', error="Пароли не совпадают")

        if get_user(username):
            return render_template('register.html', error="Такой пользователь уже существует")

        save_user(username, password)
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    generated_passwords = []
    saved = False

    if request.method == 'POST':
        if 'generate' in request.form:
            length = int(request.form.get('length', 12))
            complexity = request.form.get('complexity', 'medium')
            generated_passwords = [generate_password(length, complexity) for _ in range(5)]

        elif 'save' in request.form:
            password = request.form.get('selected_password')
            website = request.form.get('website')
            login_name = request.form.get('login')
            if password and website and login_name:
                save_password(session['user'], website, login_name, password)
                saved = True

    saved_passwords = load_passwords_for_user(session['user'])
    return render_template('index.html',
                           user=session['user'],
                           passwords=generated_passwords,
                           saved_passwords=saved_passwords,
                           saved=saved)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1337)
