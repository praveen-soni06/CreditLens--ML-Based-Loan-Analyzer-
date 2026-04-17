from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Simple demo login (minor project friendly)
        if username == 'admin' and password == 'admin123':
            return redirect(url_for('predict.application'))
        else:
            return render_template('login.html', error='Invalid username or password.')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    return redirect(url_for('auth.login'))