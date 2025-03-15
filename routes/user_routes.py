from flask import Blueprint, render_template
from flask_login import login_required, current_user

user = Blueprint('user', __name__)

@user.route('/user/dashboard')
@login_required
def dashboard():
    if current_user.role != 'user':
        return "Akses ditolak", 403
    return render_template('user_dashboard.html')
