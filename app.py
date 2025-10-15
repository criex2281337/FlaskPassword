from flask import Flask, render_template, request, redirect, url_for, session
import random, string, json
import os

app = Flask(__name__)
app.secret_key = 'secret'

accs = json.loads('[{"name":"admin","password":"12345"},{"name":"ivan","password":"qwerty"},{"name":"olga","password":"pass2025"}]')
log = 'generated_passwords.txt'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        for a in accs:
            if a['name'] == u and a['password'] == p:
                session['user'] = u
                return redirect(url_for('index'))
        return render_template('login.html', error="Неверный логин или пароль")
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    pwds = []
    if request.method == 'POST':
        try:
            length = int(request.form.get('length', 12))
        except:
            length = 12
        length = max(6, min(50, length))
        chars = string.ascii_letters + string.digits + "!@#$%"
        for _ in range(5):
            pwds.append(''.join(random.choice(chars) for _ in range(length)))
        with open(log, 'a', encoding='utf-8') as f:
            f.write(session['user'] + ' ' + ' '.join(pwds) + '\n')
    return render_template('index.html', passwords=pwds, user=session['user'])

if __name__ == '__main__':
    if not os.path.exists(log):
        open(log, 'w', encoding='utf-8').close()
    app.run(debug=True)
