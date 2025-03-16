from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
from flask_login import login_required, current_user, LoginManager
from dotenv import load_dotenv
import nltk
import os
import json
import random
import pickle
import numpy as np
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from routes.chat_routes import chat_bp
from routes.pengaduan_routes import pengaduan_bp
from routes.antrian_routes import antrian_bp
from auth import auth, load_user, bcrypt

# Pastikan hanya perlu mengunduh saat pertama kali setup
nltk.download('punkt')
nltk.download('wordnet')

# Inisialisasi lemmatizer
lemmatizer = WordNetLemmatizer()

# Nonaktifkan OneDNN jika menyebabkan error
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Load model dan data
load_dotenv
model = load_model('model.keras')
intents = json.loads(open('data.json').read())
words = pickle.load(open('texts.pkl', 'rb'))
classes = pickle.load(open('labels.pkl', 'rb'))

# Fungsi membersihkan input pengguna
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words if word.isalpha()]
    return sentence_words

# Mengubah input menjadi bag-of-words
def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [1 if w in sentence_words else 0 for w in words]
    return np.array(bag)

# Prediksi kelas intent dari input pengguna
def predict_class(sentence):
    p = bow(sentence, words)
    if np.all(p == 0):  # Jika tidak ada kata yang dikenali
        return []
    
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]

# Mendapatkan respons berdasarkan intent
def getResponse(ints):
    if not ints:
        return "Maaf, saya tidak memahami pertanyaan Anda."
    tag = ints[0]['intent']
    for intent in intents['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    return "Maaf, saya tidak memahami pertanyaan Anda."

# Fungsi utama chatbot
def chatbot_response(msg):
    ints = predict_class(msg)
    return getResponse(ints)

# Flask App
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')
CORS(app)

# Inisialisasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)  # Hubungkan dengan Flask app
login_manager.login_view = "auth.login"
login_manager.user_loader(load_user)

# Inisialisasi Bcrypt
bcrypt.init_app(app)

@app.route("/")
@login_required
def home():
    if current_user.role == 'user':
        return render_template('index.html')
    elif current_user.role == 'admin':
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('auth.login'))

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg', '').strip()
    if not userText:
        return "Silakan ketik sesuatu untuk saya jawab."
    return chatbot_response(userText)

app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(pengaduan_bp, url_prefix='/pengaduan')
app.register_blueprint(antrian_bp, url_prefix='/antrian')
app.register_blueprint(auth, url_prefix='/auth')

if __name__ == "__main__":
    app.run(debug=True)
