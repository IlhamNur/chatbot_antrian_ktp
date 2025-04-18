import psycopg2
from flask_bcrypt import Bcrypt
from config import get_db_connection
import json

bcrypt = Bcrypt()

def create_tables():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS public.users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role VARCHAR(10) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS public.antrian_ktp (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            nama VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            nomor_antrian INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'Menunggu',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS public.chat_history (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS public.pengaduan (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            nama VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            kategori VARCHAR(50) NOT NULL,
            isi_pengaduan TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS public.data (
            id SERIAL PRIMARY KEY,
            tag VARCHAR(1000) NOT NULL,
            patterns VARCHAR(1000) NOT NULL,
            responses VARCHAR(1000) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                for query in queries:
                    cursor.execute(query)
            conn.commit()
        print("Tabel berhasil dibuat atau sudah ada.")
    except psycopg2.Error as e:
        print(f"Error saat membuat tabel: {e}")

def seed_admin():
    admin_email = "admin1@example.com"
    admin_password = "admin123"
    hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (admin_email,))
                if cursor.fetchone() is None:
                    cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, 'admin')",
                                   (admin_email, hashed_password))
                    conn.commit()
                    print("Admin berhasil ditambahkan.")
                else:
                    print("Admin sudah ada, tidak perlu menambahkan lagi.")
    except psycopg2.Error as e:
        print(f"Error saat menambahkan admin: {e}")
        
def seed_data_from_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Kosongkan dulu isi tabel
                cursor.execute("DELETE FROM data")

                for item in data['intents']:
                    tag = item['tag']
                    patterns = "|".join(item['patterns'])[:1000]  # pastikan tidak melebihi kolom varchar
                    responses = "|".join(item['responses'])[:1000]

                    cursor.execute("""
                        INSERT INTO data (tag, patterns, responses)
                        VALUES (%s, %s, %s)
                    """, (tag, patterns, responses))

                conn.commit()
                print("Data berhasil di-seed dari data.json ke tabel 'data'.")

    except (psycopg2.Error, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error saat melakukan seed data: {e}")

if __name__ == "__main__":
    create_tables()
    seed_admin()
    seed_data_from_json('data.json')
