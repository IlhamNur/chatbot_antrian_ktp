import nltk
import json
import pickle
import numpy as np
import random
import tensorflow as tf
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from config import get_db_connection

def export_chatbot_data_to_json(output_file):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Ambil semua data dari tabel
                cur.execute("SELECT tag, patterns, responses FROM data")
                rows = cur.fetchall()

        intents = []

        for tag, patterns_str, responses_str in rows:
            patterns = patterns_str.split('|')
            responses = responses_str.split('|')
            intents.append({
                'tag': tag,
                'patterns': patterns,
                'responses': responses
            })

        # Tambahkan default response
        result = {
            "intents": intents
        }

        # Simpan ke file JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Data chatbot berhasil diekspor ke file '{output_file}'")

    except Exception as e:
        print(f"Gagal mengekspor data: {e}")

def train_data():
    # Download resources jika belum tersedia
    nltk.download('punkt')
    nltk.download('wordnet')

    # Coba download stopwords jika belum ada
    try:
        nltk.download('stopwords')
        stop_words = set(stopwords.words('english'))
    except:
        stop_words = set()

    lemmatizer = WordNetLemmatizer()
    ignore_words = {'?', '!', '.', ','}
    
    export_chatbot_data_to_json('data.json')

    # Load intents dataset
    with open('data.json') as file:
        intents = json.load(file)

    words = []
    classes = []
    documents = []

    # Tokenisasi dan preprocessing teks
    def preprocess_text(text):
        tokens = nltk.word_tokenize(text)
        return [lemmatizer.lemmatize(w.lower()) for w in tokens if w not in ignore_words and w not in stop_words]

    # Loop untuk mengumpulkan data pelatihan
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = preprocess_text(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = sorted(set(words))
    classes = sorted(set(classes))

    # Simpan words dan classes
    pickle.dump(words, open('texts.pkl', 'wb'))
    pickle.dump(classes, open('labels.pkl', 'wb'))

    # Membuat data training
    training = []
    output_empty = [0] * len(classes)

    for doc in documents:
        bag = [1 if w in doc[0] else 0 for w in words]
        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1
        training.append([bag, output_row])

    random.shuffle(training)
    train_x = np.array([x[0] for x in training], dtype=np.float32)
    train_y = np.array([x[1] for x in training], dtype=np.float32)

    # Membangun model
    model = Sequential([
        Dense(128, input_shape=(len(train_x[0]),), activation='relu'),
        Dropout(0.5),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(len(classes), activation='softmax')
    ])

    # Kompilasi model
    model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

    # Cek apakah GPU tersedia
    if tf.config.list_physical_devices('GPU'):
        print("GPU Ditemukan! Training akan lebih cepat.")

    # Latih model
    hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

    # Simpan model
    model.save('model.keras')  # Format lebih modern
    with open('training_history.json', 'w') as f:
        json.dump(hist.history, f)

    # Simpan model dalam format JSON
    model_json = model.to_json()
    with open('model.json', 'w') as json_file:
        json_file.write(model_json)

    print("Model berhasil dibuat dan disimpan!")
    
if __name__ == "__main__":
    train_data()
