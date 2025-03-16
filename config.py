import psycopg2
import os
from dotenv import load_dotenv

# Load variabel lingkungan dari .env
load_dotenv()

# Konfigurasi Database dari Environment Variables
DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'ktp_chatbot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e.pgerror}")
        return None
