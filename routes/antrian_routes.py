from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from config import get_db_connection
from email_service import send_email
from auth import admin_required, login_required

antrian_bp = Blueprint('antrian_bp', __name__)

# Fungsi untuk mendapatkan nomor antrian terbaru
def get_next_antrian():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(nomor_antrian), 0) + 1 FROM antrian_ktp")
            return cur.fetchone()[0]

# Endpoint untuk menambahkan antrian KTP
@antrian_bp.route('/daftar', methods=['POST'])
@login_required
def daftar_antrian():
    data = request.json
    user_id = data.get('user_id')
    nama = data.get('nama')
    email = data.get('email')

    if not all([user_id, nama, email]):
        return jsonify({'error': 'Data tidak lengkap'}), 400

    nomor_antrian = get_next_antrian()

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO antrian_ktp (user_id, nama, email, nomor_antrian)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, nama, email, nomor_antrian))
                conn.commit()

        # Kirim email notifikasi
        subject = "Nomor Antrian KTP Anda"
        body = f"Halo {nama},\n\nNomor antrian KTP Anda adalah {nomor_antrian}.\nHarap datang sesuai jadwal.\n\nTerima kasih!"
        send_email(email, subject, body)

        return jsonify({'message': 'Antrian berhasil didaftarkan dan email notifikasi telah dikirim', 'nomor_antrian': nomor_antrian}), 201

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Endpoint untuk melihat semua antrian
@antrian_bp.route('/list', methods=['GET'])
@login_required
@admin_required
def list_antrian():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, user_id, nama, email, nomor_antrian, status, created_at FROM antrian_ktp ORDER BY status ASC")
                antrian = cur.fetchall()

        result = [
            {'id': a[0], 'user_id': a[1], 'nama': a[2], 'email': a[3], 'nomor_antrian': a[4], 'status': a[5], 'created_at': a[6]}
            for a in antrian
        ]

        return render_template('antrian.html', antrian=result), 200

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Endpoint untuk mengupdate status antrian
@antrian_bp.route('/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_antrian(id):
    status = request.form.get('status')

    if not status:
        return jsonify({'error': 'Status tidak boleh kosong'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Ambil nomor antrian dari ID yang ingin diupdate
                cur.execute("SELECT nomor_antrian FROM antrian_ktp WHERE id = %s", (id,))
                result = cur.fetchone()
                if result is None:
                    return jsonify({'error': 'Antrian tidak ditemukan'}), 404

                current_no = result[0]

                # Update status dan set nomor_antrian = 0
                cur.execute("""
                    UPDATE antrian_ktp
                    SET status = %s, nomor_antrian = 0
                    WHERE id = %s
                """, (status, id))

                # Geser semua antrian setelahnya
                cur.execute("""
                    UPDATE antrian_ktp
                    SET nomor_antrian = nomor_antrian - 1
                    WHERE nomor_antrian > %s
                """, (current_no,))

                conn.commit()

        return redirect(url_for('antrian_bp.list_antrian'))

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Endpoint untuk reset antrian
@antrian_bp.route('/reset', methods=['POST'])
@login_required
@admin_required
def reset_antrian():
    if request.form.get('_method') == 'DELETE':
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Hapus semua data dan reset ID (auto increment)
                    cur.execute("TRUNCATE TABLE antrian_ktp RESTART IDENTITY CASCADE")
                    conn.commit()
                    
            flash('Antrian berhasil direset', 'success')
            return redirect(url_for('antrian_bp.list_antrian'))

        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('antrian_bp.list_antrian'))
                            
    return jsonify({'error': 'Method Not Allowed'}), 405
