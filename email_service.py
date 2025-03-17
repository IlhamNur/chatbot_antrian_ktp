from flask_mail import Mail, Message
from flask import Flask
import os

app = Flask(__name__)

# Konfigurasi SMTP Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')  # Set di environment variable
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')  # Set di environment variable

mail = Mail(app)

def send_email(recipient, subject, body):
    try:
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
        msg.body = body
        with app.app_context():
            mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
