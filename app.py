from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
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

# Pastikan hanya perlu mengunduh saat pertama kali setup
nltk.download('punkt')
nltk.download('wordnet')

# Inisialisasi lemmatizer
lemmatizer = WordNetLemmatizer()

# Nonaktifkan OneDNN jika menyebabkan error
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Load dotenv
load_dotenv()

# Load model dan data dengan pengecekan
MODEL_PATH = 'model.h5'
DATA_PATH = 'data.json'
TEXTS_PATH = 'texts.pkl'
LABELS_PATH = 'labels.pkl'

if os.path.exists(MODEL_PATH):
    model = load_model(MODEL_PATH)
else:
    raise FileNotFoundError(f"Model tidak ditemukan: {MODEL_PATH}")

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    intents = json.load(f)

with open(TEXTS_PATH, 'rb') as f:
    words = pickle.load(f)

with open(LABELS_PATH, 'rb') as f:
    classes = pickle.load(f)

# Fungsi membersihkan input pengguna
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words if word.isalpha()]

# Mengubah input menjadi bag-of-words
def bow(sentence, words):
    sentence_words = set(clean_up_sentence(sentence))  # Gunakan set untuk pencarian lebih cepat
    return np.array([1 if w in sentence_words else 0 for w in words])

# Prediksi kelas intent dari input pengguna
def predict_class(sentence):
    p = bow(sentence, words)
    if np.all(p == 0):  # Jika tidak ada kata yang dikenali
        return []

    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = sorted(
        [(classes[i], prob) for i, prob in enumerate(res) if prob > ERROR_THRESHOLD],
        key=lambda x: x[1],
        reverse=True
    )
    return [{"intent": intent, "probability": str(prob)} for intent, prob in results]

# Mendapatkan respons berdasarkan intent
def get_response(ints):
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
    return get_response(ints)

# Flask App
app = Flask(__name__, static_url_path='/static')
CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Optimasi JSON output

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg', '').strip()
    if not user_text:
        return jsonify({'response': "Silakan ketik sesuatu untuk saya jawab."})
    return jsonify({'response': chatbot_response(user_text)})

# Register Blueprint
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(pengaduan_bp, url_prefix='/pengaduan')
app.register_blueprint(antrian_bp, url_prefix='/antrian')

if __name__ == "__main__":
    app.run(debug=True)
