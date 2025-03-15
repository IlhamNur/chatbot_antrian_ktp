from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from config import get_db_connection
from email_service import send_email

antrian_bp = Blueprint('antrian_bp', __name__)

# Fungsi untuk mendapatkan nomor antrian terbaru
def get_next_antrian():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(nomor_antrian), 0) + 1 FROM antrian_ktp")
    next_number = cur.fetchone()[0]
    cur.close()
    conn.close()
    return next_number

# Endpoint untuk menambahkan antrian KTP
@antrian_bp.route('/daftar', methods=['POST'])
def daftar_antrian():
    data = request.json
    user_id = data.get('user_id')
    nama = data.get('nama')
    email = data.get('email')

    if not all([user_id, nama, email]):
        return jsonify({'error': 'Data tidak lengkap'}), 400

    nomor_antrian = get_next_antrian()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO antrian_ktp (user_id, nama, email, nomor_antrian)
        VALUES (%s, %s, %s, %s)
    """, (user_id, nama, email, nomor_antrian))
    conn.commit()
    cur.close()
    conn.close()

    # Kirim email notifikasi
    subject = "Nomor Antrian KTP Anda"
    body = f"Halo {nama},\n\nNomor antrian KTP Anda adalah {nomor_antrian}.\nHarap datang sesuai jadwal.\n\nTerima kasih!"
    send_email(email, subject, body)

    return jsonify({'message': 'Antrian berhasil didaftarkan dan email notifikasi telah dikirim', 'nomor_antrian': nomor_antrian}), 201

# Endpoint untuk melihat semua antrian
@antrian_bp.route('/list', methods=['GET'])
def list_antrian():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, nama, email, nomor_antrian, status, created_at FROM antrian_ktp ORDER BY created_at ASC")
    antrian = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for a in antrian:
        result.append({
            'id': a[0],
            'user_id': a[1],
            'nama': a[2],
            'email': a[3],
            'nomor_antrian': a[4],
            'status': a[5],
            'created_at': a[6]
        })

    return render_template('antrian.html', antrian=result), 200

# Endpoint untuk mengupdate status antrian
@antrian_bp.route('/update/<int:id>', methods=['PUT'])
def update_antrian(id):
    data = request.json
    status = data.get('status')

    if not status:
        return jsonify({'error': 'Status tidak boleh kosong'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE antrian_ktp SET status = %s WHERE id = %s", (status, id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Status antrian diperbarui'}), 200

# Endpoint untuk reset antrian
@antrian_bp.route('/reset', methods=['DELETE'])
def reset_antrian():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM antrian_ktp")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('antrian_bp.list_antrian'), jsonify({'message': 'Antrian berhasil direset'})), 200
