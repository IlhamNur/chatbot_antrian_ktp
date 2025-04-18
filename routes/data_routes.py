from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from config import get_db_connection
from auth import admin_required, login_required
from training import train_data

data_bp = Blueprint('data_bp', __name__)

# Endpoint untuk menambahkan data
@data_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add_chatbot_data():
    data = request.form
    tag = data.get('tag')
    patterns = request.form.get('patterns', '').splitlines()
    patterns = [p.strip() for p in patterns if p.strip()]

    responses = request.form.get('responses', '').splitlines()
    responses = [r.strip() for r in responses if r.strip()]


    if not all([tag, patterns, responses]):
        flash('Data tidak lengkap. Mohon isi tag, pola, dan respon', 'danger')
        return redirect(url_for('data_bp.list_chatbot_data'))

    try:
        patterns_str = "|".join(patterns)[:1000]
        responses_str = "|".join(responses)[:1000]

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO data (tag, patterns, responses)
                    VALUES (%s, %s, %s)
                """, (tag, patterns_str, responses_str))
                conn.commit()
                
        train_data()

        flash('Data chatbot berhasil ditambahkan', 'success')
        return redirect(url_for('data_bp.list_chatbot_data'))

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# Endpoint untuk melihat semua data chatbot
@data_bp.route('/list', methods=['GET'])
@login_required
@admin_required
def list_chatbot_data():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, tag, patterns, responses, created_at
                    FROM data
                    ORDER BY created_at ASC
                """)
                rows = cur.fetchall()

        result = [
            {
                'id': row[0],
                'tag': row[1],
                'patterns': row[2].split('|'),     # konversi string ke list
                'responses': row[3].split('|'),    # konversi string ke list
                'created_at': row[4]
            }
            for row in rows
        ]

        return render_template('chatbot.html', data=result), 200

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

@data_bp.route('/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_chatbot_data(id):
    data = request.form
    tag = data.get('tag')
    raw_patterns = data.get('patterns', '')
    raw_responses = data.get('responses', '')

    # Konversi string menjadi list (pisah berdasarkan baris atau koma)
    patterns = [p.strip() for p in raw_patterns.replace('\r', '').split('\n') if p.strip()]
    responses = [r.strip() for r in raw_responses.replace('\r', '').split('\n') if r.strip()]

    if not all([tag, patterns, responses]):
        flash('Data tidak lengkap. Mohon isi tag, pola, dan respon', 'danger')
        return redirect(url_for('data_bp.list_chatbot_data'))

    try:
        patterns_str = "|".join(patterns)[:1000]
        responses_str = "|".join(responses)[:1000]

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE data
                    SET tag = %s,
                        patterns = %s,
                        responses = %s
                    WHERE id = %s
                """, (tag, patterns_str, responses_str, id))
                conn.commit()

        # retraining model
        train_data()

        flash('Data chatbot berhasil diubah', 'success')
        return redirect(url_for('data_bp.list_chatbot_data'))

    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('data_bp.list_chatbot_data'))


@data_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_chatbot_data(id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM data WHERE id = %s", (id,))
                conn.commit()

        train_data()
        
        flash('Data chatbot berhasil dihapus', 'success')
        return redirect(url_for('data_bp.list_chatbot_data'))

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500
