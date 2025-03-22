from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from config import get_db_connection
from token_module import generate_reset_token, verify_reset_token
from email_service import send_email
import psycopg2

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role


def admin_required(func):
    """Dekorator untuk memastikan hanya admin yang bisa mengakses route"""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # Agar Flask bisa mengenali nama fungsi asli
    return wrapper

# Fungsi user_loader untuk Flask-Login
def load_user(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, email, role FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                if user:
                    return User(user[0], user[1], user[2])
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, 'user')", (email, password))
                    conn.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('auth.login'))
        except psycopg2.Error as e:
            flash(f'Error: {e.pgerror}', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, email, password, role FROM users WHERE email = %s", (email,))
                    user = cursor.fetchone()

                    if user and bcrypt.check_password_hash(user[2], password):
                        user_obj = User(user[0], user[1], user[3])
                        login_user(user_obj)
                        session['role'] = user[3]

                        return redirect(url_for('home'))
        except psycopg2.Error as e:
            flash(f'Error: {e.pgerror}', 'danger')

        flash('Email atau password salah!', 'danger')

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('role', None)
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']

        if not email:
            return jsonify({'error': 'Email diperlukan'}), 400

        token = generate_reset_token(email)
        reset_url = url_for('auth.reset_password', token=token, _external=True)

        try:
            subject = "Reset Password"
            body = f"Klik link berikut untuk mengatur ulang kata sandi Anda: {reset_url}"
            send_email(email, subject, body)
            flash('Email reset password telah dikirim', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            return jsonify({'error': f'Terjadi kesalahan saat mengirim email: {str(e)}'}), 500
    
    return render_template('lupa_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        return jsonify({'error': 'Token tidak valid atau sudah kadaluarsa'}), 400

    if request.method == 'POST':
        new_password = request.form['password']

        if not new_password:
            return jsonify({'error': 'Password baru diperlukan'}), 400

        # Simpan password baru ke database (hashing sebelum menyimpan)
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
                conn.commit()

        flash('Password berhasil direset', 'success')
        return redirect(url_for('home'))
    
    return render_template('reset_password.html', token=token)
