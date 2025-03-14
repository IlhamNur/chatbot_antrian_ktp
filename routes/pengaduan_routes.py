from flask import Blueprint, request, jsonify
from config import get_db_connection
from email_service import send_email

pengaduan_bp = Blueprint('pengaduan_bp', __name__)

# Endpoint untuk menambahkan pengaduan
@pengaduan_bp.route('/add', methods=['POST'])
def add_pengaduan():
    data = request.json
    user_id = data.get('user_id')
    nama = data.get('nama')
    email = data.get('email')
    kategori = data.get('kategori')
    isi_pengaduan = data.get('isi_pengaduan')

    if not all([user_id, nama, email, kategori, isi_pengaduan]):
        return jsonify({'error': 'Data tidak lengkap'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pengaduan (user_id, nama, email, kategori, isi_pengaduan)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, nama, email, kategori, isi_pengaduan))
    conn.commit()
    cur.close()
    conn.close()

    # Kirim notifikasi email ke pengguna
    subject = "Konfirmasi Pengaduan Anda"
    body = f"Halo {nama},\n\nPengaduan Anda dengan kategori '{kategori}' telah diterima.\nKami akan segera menindaklanjuti.\n\nTerima kasih!"
    send_email(email, subject, body)

    return jsonify({'message': 'Pengaduan berhasil dikirim dan email notifikasi telah dikirim'}), 201

# Endpoint untuk melihat semua pengaduan
@pengaduan_bp.route('/list', methods=['GET'])
def list_pengaduan():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, nama, email, kategori, isi_pengaduan, status, created_at FROM pengaduan ORDER BY created_at DESC")
    pengaduan = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for p in pengaduan:
        result.append({
            'id': p[0],
            'user_id': p[1],
            'nama': p[2],
            'email': p[3],
            'kategori': p[4],
            'isi_pengaduan': p[5],
            'status': p[6],
            'created_at': p[7]
        })

    return jsonify({'pengaduan': result}), 200

# Endpoint untuk mengupdate status pengaduan
@pengaduan_bp.route('/update/<int:id>', methods=['PUT'])
def update_pengaduan(id):
    data = request.json
    status = data.get('status')

    if not status:
        return jsonify({'error': 'Status tidak boleh kosong'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE pengaduan SET status = %s WHERE id = %s", (status, id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Status pengaduan diperbarui'}), 200
