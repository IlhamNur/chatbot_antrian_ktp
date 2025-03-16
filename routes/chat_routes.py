from flask import Blueprint, request, jsonify, render_template
from config import get_db_connection

chat_bp = Blueprint('chat_bp', __name__)

# Endpoint untuk menambahkan chat ke dalam history
@chat_bp.route('/add', methods=['POST'])
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
def history():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT message, response, timestamp FROM chat_history ORDER BY timestamp ASC")
                chats = cur.fetchall()

        result = [{'message': c[0], 'response': c[1], 'timestamp': c[2]} for c in chats]

        return render_template('history.html', history=result), 200

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500
