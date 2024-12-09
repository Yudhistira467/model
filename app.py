from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Inisialisasi Firebase
cred = credentials.Certificate("./answer-service-account.json")  # Ganti dengan path ke file credentials Anda
firebase_admin.initialize_app(cred)

# Load model machine learning Anda
model = load_model('./model/recommendation_model.h5')  # Ganti dengan path ke model .h5 Anda

# Mengambil referensi ke Firestore
db = firestore.client()

# Endpoint untuk memproses data dan memberikan prediksi
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Ambil user_id dari request JSON
        user_id = request.json.get('user_id')

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Ambil jawaban pengguna dari Firestore
        user_answers_ref = db.collection('user_answer').where('userId', '==', user_id)
        user_answers = user_answers_ref.stream()

        # Mengambil dan mengolah data untuk model
        answers_data = []
        for doc in user_answers:
            answers = doc.to_dict().get('answers', [])
            for answer in answers:
                user_answer = answer.get('userAnswer')
                is_correct = answer.get('isCorrect')
                question_id = answer.get('questionId')
                if question_id is not None:
                    answers_data.append(int(question_id))

        if not answers_data:
            return jsonify({"error": "No data found for user"}), 404

        # Padding input agar panjangnya sesuai dengan model
        padded_input_data = np.zeros(2000)
        padded_input_data[:len(answers_data)] = answers_data
        
        # Ubah data ke bentuk yang bisa diproses model
        X = np.expand_dims(padded_input_data, axis=0)
        
        # Prediksi dengan model
        predictions = model.predict(X)
        
        # Misalnya hasil prediksi diolah menjadi kelas atau probabilitas
        results = predictions.tolist()

        return jsonify({"predictions": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)