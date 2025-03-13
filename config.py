import psycopg2

DATABASE_CONFIG = {
    'dbname': 'ktp_chatbot',
    'user': 'postgres',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn
