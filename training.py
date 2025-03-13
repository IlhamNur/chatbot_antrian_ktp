import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import json
import pickle
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam

# Download resources jika belum tersedia
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Load intents dataset
words = []
classes = []
documents = []
ignore_words = ['?', '!', '.', ',']

with open('data.json') as file:
    intents = json.load(file)

# Process intents
for intent in intents['intents']:
    for pattern in intent['patterns']:
        # Tokenize and preprocess
        w = nltk.word_tokenize(pattern)
        w = [lemmatizer.lemmatize(word.lower()) for word in w if word not in ignore_words and word not in stop_words]
        words.extend(w)
        documents.append((w, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = sorted(set(words))
classes = sorted(set(classes))

# Save words and classes
pickle.dump(words, open('texts.pkl', 'wb'))
pickle.dump(classes, open('labels.pkl', 'wb'))

# Create training data
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

# Build model
model = Sequential([
    Dense(128, input_shape=(len(train_x[0]),), activation='relu'),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(len(classes), activation='softmax')
])

# Compile model
model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

# Train model
hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

# Save model
model.save('model.h5')
with open('training_history.json', 'w') as f:
    json.dump(hist.history, f)

# Save model architecture
model_json = model.to_json()
with open('model.json', 'w') as json_file:
    json_file.write(model_json)

print("Model created and saved successfully")
