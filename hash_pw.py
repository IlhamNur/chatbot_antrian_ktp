from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
hashed_pw = bcrypt.generate_password_hash("password123").decode('utf-8')
print(hashed_pw)
