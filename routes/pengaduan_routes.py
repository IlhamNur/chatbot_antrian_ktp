from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from config import get_db_connection
from email_service import send_email
from auth import admin_required, login_required

pengaduan_bp = Blueprint('pengaduan_bp', __name__)

# Endpoint untuk menambahkan pengaduan
@pengaduan_bp.route('/add', methods=['POST'])
@login_required
def add_pengaduan():
    data = request.json
    user_id = data.get('user_id')
    nama = data.get('nama')
    email = data.get('email')
    kategori = data.get('kategori')
    isi_pengaduan = data.get('isi_pengaduan')

    if not all([user_id, nama, email, kategori, isi_pengaduan]):
        return jsonify({'error': 'Data tidak lengkap'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO pengaduan (user_id, nama, email, kategori, isi_pengaduan)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, nama, email, kategori, isi_pengaduan))
                conn.commit()

        # Kirim notifikasi email ke pengguna
        subject = "Konfirmasi Pengaduan Anda"
        body = f"Halo {nama},\n\nPengaduan Anda dengan kategori '{kategori}' telah diterima.\nKami akan segera menindaklanjuti.\n\nTerima kasih!"
        send_email(email, subject, body)

        return jsonify({'message': 'Pengaduan berhasil dikirim dan email notifikasi telah dikirim'}), 201

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Endpoint untuk melihat semua pengaduan
@pengaduan_bp.route('/list', methods=['GET'])
@login_required
@admin_required
def list_pengaduan():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, user_id, nama, email, kategori, isi_pengaduan, status, created_at FROM pengaduan ORDER BY created_at DESC")
                pengaduan = cur.fetchall()

        result = [
            {
                'id': p[0],
                'user_id': p[1],
                'nama': p[2],
                'email': p[3],
                'kategori': p[4],
                'isi_pengaduan': p[5],
                'status': p[6],
                'created_at': p[7]
            }
            for p in pengaduan
        ]

        return render_template('admin_dashboard.html', pengaduan=result), 200

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Endpoint untuk mengupdate status pengaduan
@pengaduan_bp.route('/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_pengaduan(id):
    status = request.form.get('status')

    if not status:
        return jsonify({'error': 'Status tidak boleh kosong'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE pengaduan SET status = %s WHERE id = %s RETURNING email, kategori", (status, id))
                pengaduan = cur.fetchone()
                conn.commit()

        if pengaduan and status.lower() == 'selesai':
            email_penerima, kategori = pengaduan
            subject = "Pengaduan Anda Telah Disetujui"
            body = f"Halo,\n\nPengaduan Anda terkait '{kategori}' telah selesai diproses. Terima kasih atas partisipasi Anda.\n\nSalam,\nAdmin"
            send_email(email_penerima, subject, body)

        return redirect(url_for('pengaduan_bp.list_pengaduan'))  # Redirect agar halaman reload

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

