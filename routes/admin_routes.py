from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('app.home'))
    return render_template('admin_dashboard.html')
