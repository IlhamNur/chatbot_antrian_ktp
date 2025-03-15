from flask import Blueprint, request, jsonify, render_template
from config import get_db_connection

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/add', methods=['POST'])
def add_chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    response = data.get('response')

    if not user_id or not message or not response:
        return jsonify({'error': 'Data tidak lengkap'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chat_history (user_id, message, response)
        VALUES (%s, %s, %s)
    """, (user_id, message, response))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Chat berhasil disimpan'}), 201

@chat_bp.route('/get/<user_id>', methods=['GET'])
def get_chat(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT message, response, timestamp FROM chat_history WHERE user_id = %s", (user_id,))
    chats = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({'history': chats}), 200

@chat_bp.route('/get', methods=['GET'])
def history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT message, response, timestamp FROM chat_history")
    chats = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('history.html', history=chats), 200