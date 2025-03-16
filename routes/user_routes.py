from flask import Blueprint, render_template, abort, flash
from flask_login import login_required, current_user

user = Blueprint('user', __name__)

@user.route('/user/dashboard')
@login_required
def dashboard():
    if current_user.role != 'user':
        flash("Akses ditolak: Anda tidak memiliki izin untuk mengakses halaman ini.", "danger")
        abort(403)  # Menggunakan abort untuk response standar HTTP 403
    return render_template('index.html')
