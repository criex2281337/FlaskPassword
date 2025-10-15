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
        with open(USERS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    name, password = line.strip().split(' ', 1)
                    users[name] = password
    return users

def save_user(name, password):
    with open(USERS_FILE, 'a') as f:
        f.write(f"{name} {password}\n")

def save_passwords(name, website, passwords):
    with open(PASSWORDS_FILE, 'a') as f:
        f.write(f"{name} | {website} | {' '.join(passwords)}\n")

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
        complexity = request.form.get('complexity', 'medium')
        website = request.form.get('website', 'Не указан')
        
        for _ in range(5):
            password = generate_password(length, complexity)
            passwords.append(password)

        save_passwords(session['user'], website, passwords)

    return render_template('index.html', passwords=passwords, user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
