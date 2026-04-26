from flask import Blueprint, render_template, request, redirect, url_for, session
from app.database.db import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET'])
def root():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Support both old frontend (username) and new frontend (email)
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Prefer email if provided, otherwise fallback for old UI
        user = None

        if email:
            user = User.query.filter_by(email=email).first()
        elif username:
            # Allow old demo style login by matching name or special admin shortcut
            user = User.query.filter_by(name=username).first()

            # Extra fallback for your old demo login form
            if not user and username.lower() == 'admin':
                user = User.query.filter_by(email='admin@creditlens.com').first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['role'] = user.role

            # Role-based redirect
            if user.role == 'credit_manager':
                return redirect(url_for('dashboard.dashboard'))
            else:
                return redirect(url_for('predict.application'))

        return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))