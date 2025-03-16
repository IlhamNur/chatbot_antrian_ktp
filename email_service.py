from flask_mail import Mail, Message
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()  # Memuat variabel dari .env

mail = Mail()

def create_app():
    app = Flask(__name__)

    # Konfigurasi Email dari Environment Variables
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')  # Default sender

    mail.init_app(app)
    
    return app

def send_email(recipient, subject, body):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        with mail.connect() as conn:
            conn.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
