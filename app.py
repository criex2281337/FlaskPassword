from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
import os

app = Flask(__name__)
app.secret_key = 'secret'

USERS_FILE = 'users.txt'
PASSWORDS_FILE = 'passwords.txt'

# ────────────────────────────────
# Работа с пользователями
# ────────────────────────────────
def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    name, password = line.strip().split(' ', 1)
                    users[name] = password
    return users

def save_user(name, password):
    with open(USERS_FILE, 'a') as f:
        f.write(f"{name} {password}\n")

# ────────────────────────────────
# Работа с паролями
# ────────────────────────────────
def save_password(name, website, login, password):
    with open(PASSWORDS_FILE, 'a') as f:
        f.write(f"{name} | {website} | {login} | {password}\n")

def load_passwords_for_user(name):
    passwords = []
    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(' | ')
                    if len(parts) == 4 and parts[0] == name:
                        _, website, login, password = parts
                        passwords.append((website, login, password))
    return passwords

# ────────────────────────────────
# Генерация паролей
# ────────────────────────────────
def generate_password(length, complexity):
    if complexity == 'simple':
        chars = string.ascii_letters + string.digits
    elif complexity == 'medium':
        chars = string.ascii_letters + string.digits + "!@#$%"
    else:
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(random.choice(chars) for _ in range(length))

# ────────────────────────────────
# Роуты
# ────────────────────────────────
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
                           user=session['user'],passwords=generated_passwords,
                           saved_passwords=saved_passwords,
                           saved=saved)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1337)
