from itsdangerous import URLSafeTimedSerializer
import os

SECRET_KEY = os.getenv('SECRET_KEY')

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt="reset-password-salt")

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt="reset-password-salt", max_age=expiration)
    except:
        return None
    return email
