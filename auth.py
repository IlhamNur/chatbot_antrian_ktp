from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2
import os

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()
login_manager = LoginManager()

# Koneksi database
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

class User(UserMixin):
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT id, email, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user[0], user[1], user[2])
    return None

# Register untuk user biasa
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        try:
            cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, 'user')", (email, password))
            conn.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('auth.login'))
        except:
            flash('Email sudah terdaftar.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

# Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT id, email, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[2], password):
            user_obj = User(user[0], user[1], user[3])
            login_user(user_obj)
            session['role'] = user[3]

            if user[3] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        
        flash('Email atau password salah!', 'danger')
    
    return render_template('login.html')

# Logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('role', None)
    return redirect(url_for('auth.login'))
