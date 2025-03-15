from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return "Akses ditolak", 403
    return render_template('admin_dashboard.html')
