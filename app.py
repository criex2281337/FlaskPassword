from flask import Flask, render_template, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key = 'secret'

USERNAME = 'admin'
PASSWORD = '12345'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            print(f"{session['user']}")
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверный логин или пароль")

    return render_template('login.html')


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

    return render_template('index.html', passwords=passwords, user=session['user'])


if __name__ == '__main__':
    app.run(debug=True)
