from flask import Flask, render_template, request
import random
import string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():



    passwords = []

    if request.method == 'POST':
        length = int(request.form.get('length', 12))
        
        for _ in range(5):
            chars = string.ascii_letters + string.digits + "!@#$%"
            password = ''.join(random.choice(chars) for _ in range(length))
            passwords.append(password)
    
    return render_template('index.html', passwords=passwords)


if __name__ == '__main__':
    app.run(debug=True)
