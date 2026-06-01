from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Change this
    'database': 'disease_prediction'
}

# Load ML models
try:
    model = joblib.load('models/disease_model.pkl')
    label_encoder = joblib.load('models/label_encoder.pkl')
    symptoms_list = joblib.load('models/symptom_list.pkl')
    print("Models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    model = None
    label_encoder = None
    symptoms_list = []

# Database connection function
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Routes
@app.route('/')
def index():
    return render_template('index.html', symptoms=symptoms_list)

@app.route('/predict')
def predict_page():
    return render_template('predict.html', symptoms=symptoms_list)

@app.route('/records')
def records_page():
    return render_template('records.html')

# API: Get symptoms list
@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify({'symptoms': symptoms_list})

# API: Predict disease
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        patient_name = data.get('patient_name')
        age = data.get('age')
        gender = data.get('gender')
        contact = data.get('contact')
        selected_symptoms = data.get('symptoms', [])
        
        if not selected_symptoms:
            return jsonify({'error': 'Please select at least one symptom'}), 400
        
        # Create feature vector
        feature_vector = []
        for symptom in symptoms_list:
            feature_vector.append(1 if symptom in selected_symptoms else 0)
        
        # Make prediction
        features = np.array([feature_vector])
        prediction_encoded = model.predict(features)[0]
        confidence_scores = model.predict_proba(features)[0]
        confidence = max(confidence_scores) * 100
        predicted_disease = label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert patient
        cursor.execute(
            "INSERT INTO patients (name, age, gender, contact) VALUES (%s, %s, %s, %s)",
            (patient_name, age, gender, contact)
        )
        patient_id = cursor.lastrowid
        
        # Insert prediction
        symptoms_filled = selected_symptoms + [''] * (5 - len(selected_symptoms))
        cursor.execute("""
            INSERT INTO predictions 
            (patient_id, symptom_1, symptom_2, symptom_3, symptom_4, symptom_5, 
             predicted_disease, confidence_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (patient_id, *symptoms_filled[:5], predicted_disease, confidence))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'predicted_disease': predicted_disease,
            'confidence': round(confidence, 2),
            'patient_id': patient_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get prediction records
@app.route('/api/records', methods=['GET'])
def get_records():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.id, p.name, p.age, p.gender, p.contact,
                   pr.predicted_disease, pr.confidence_score, pr.prediction_date,
                   pr.symptom_1, pr.symptom_2, pr.symptom_3, pr.symptom_4, pr.symptom_5
            FROM patients p
            JOIN predictions pr ON p.id = pr.patient_id
            ORDER BY pr.prediction_date DESC
        """)
        
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format records
        for record in records:
            symptoms = []
            for i in range(1, 6):
                symptom = record.get(f'symptom_{i}')
                if symptom and symptom.strip():
                    symptoms.append(symptom)
            record['symptoms_list'] = symptoms
            record['prediction_date'] = record['prediction_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'records': records})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)