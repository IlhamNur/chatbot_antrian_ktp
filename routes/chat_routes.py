from flask import Blueprint, request, jsonify, render_template, redirect
from config import get_db_connection
from auth import admin_required, login_required

chat_bp = Blueprint('chat_bp', __name__)

# Endpoint untuk menambahkan chat ke dalam history
@chat_bp.route('/add', methods=['POST'])
@login_required
def add_chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    response = data.get('response')

    if not all([user_id, message, response]):
        return jsonify({'error': 'Data tidak lengkap'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_history (user_id, message, response)
                    VALUES (%s, %s, %s)
                """, (user_id, message, response))
                conn.commit()
        
        return jsonify({'message': 'Chat berhasil disimpan'}), 201

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Endpoint untuk mendapatkan chat history berdasarkan user_id
@chat_bp.route('/get/<user_id>', methods=['GET'])
@login_required
def get_chat(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT message, response, timestamp FROM chat_history WHERE user_id = %s ORDER BY timestamp ASC", (user_id,))
                chats = cur.fetchall()

        if not chats:
            return jsonify({'message': 'Tidak ada riwayat chat untuk user ini'}), 404

        result = [{'message': c[0], 'response': c[1], 'timestamp': c[2]} for c in chats]

        return jsonify({'history': result}), 200

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Endpoint untuk mendapatkan semua chat history
@chat_bp.route('/get', methods=['GET'])
@login_required
@admin_required
def history():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Ambil daftar user unik dengan last_message_time
                cur.execute("""
                    SELECT ch.user_id, u.email, MAX(ch.timestamp) AS last_message_time
                    FROM chat_history ch
                    JOIN users u ON CAST(ch.user_id AS INTEGER) = u.id
                    GROUP BY ch.user_id, u.email
                    ORDER BY last_message_time DESC
                """)
                users = cur.fetchall()

                user_chat_data = []

                for user in users:
                    user_id, email, last_message_time = user
                    
                    # Ambil semua message dan response untuk setiap user_id
                    cur.execute("""
                        SELECT message, response, timestamp 
                        FROM chat_history 
                        WHERE user_id = %s 
                        ORDER BY timestamp ASC
                    """, (user_id,))
                    chats = cur.fetchall()

                    chat_history = [
                        {'message': c[0], 'response': c[1], 'timestamp': c[2]} for c in chats
                    ]

                    user_chat_data.append({
                        'user_id': user_id,
                        'email': email,
                        'last_message_time': last_message_time,
                        'chats': chat_history  # Semua chat dari user ini
                    })

        return render_template('history.html', users=user_chat_data), 200

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500




