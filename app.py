from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
import os

app = Flask(__name__)
app.secret_key = 'secret'

USERS_FILE = 'users.txt'
PASSWORDS_FILE = 'passwords.txt'


def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    name, password = line.strip().split(' ', 1)
                    users[name] = password
    return users


def save_user(name, password):
    with open(USERS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{name} {password}\n")


def save_passwords(name, passwords):
    with open(PASSWORDS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{name} {' '.join(passwords)}\n")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        if username in users and users[username] == password:
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

        users = load_users()
        if username in users:
            return render_template('register.html', error="Такой пользователь уже существует")

        save_user(username, password)
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    passwords = []
    if request.method == 'POST':
        length = int(request.form.get('length', 12))
        for _ in range(5):
            chars = string.ascii_letters + string.digits + "!@#$%"
            password = ''.join(random.choice(chars) for _ in range(length))
            passwords.append(password)

        save_passwords(session['user'], passwords)

    return render_template('index.html', passwords=passwords, user=session['user'])


if __name__ == '__main__':
    app.run(debug=True)
