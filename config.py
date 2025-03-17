import psycopg2
import os
from dotenv import load_dotenv

# Load variabel lingkungan dari .env
load_dotenv()

# Konfigurasi Database dari Environment Variables
DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e.pgerror}")
        return None
