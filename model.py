import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Create synthetic dataset
def create_synthetic_dataset():
    np.random.seed(42)
    n_samples = 5000
    
    # Symptoms (20 common symptoms)
    symptoms = [
        'fever', 'cough', 'fatigue', 'headache', 'nausea',
        'chest_pain', 'shortness_breath', 'joint_pain', 
        'sore_throat', 'runny_nose', 'diarrhea', 'vomiting',
        'abdominal_pain', 'dizziness', 'rash', 'muscle_ache',
        'loss_appetite', 'weight_loss', 'insomnia', 'anxiety'
    ]
    
    # Diseases mapping
    diseases = {
        'Common Cold': ['fever', 'cough', 'runny_nose', 'sore_throat', 'fatigue'],
        'Influenza': ['fever', 'cough', 'fatigue', 'muscle_ache', 'headache'],
        'COVID-19': ['fever', 'cough', 'fatigue', 'shortness_breath', 'loss_appetite'],
        'Migraine': ['headache', 'nausea', 'dizziness', 'fatigue', 'anxiety'],
        'Gastroenteritis': ['nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'fever'],
        'Arthritis': ['joint_pain', 'fatigue', 'muscle_ache', 'fatigue', 'weight_loss'],
        'Bronchitis': ['cough', 'fatigue', 'chest_pain', 'shortness_breath', 'fever'],
        'Allergy': ['runny_nose', 'sore_throat', 'rash', 'fatigue', 'headache']
    }
    
    data = []
    labels = []
    
    for _ in range(n_samples):
        # Randomly select a disease
        disease = np.random.choice(list(diseases.keys()))
        disease_symptoms = diseases[disease]
        
        # Create symptom vector (0 or 1 for each symptom)
        symptom_vector = []
        for symptom in symptoms:
            if symptom in disease_symptoms:
                # Core symptoms have 90% chance of being present
                symptom_vector.append(1 if np.random.random() < 0.9 else 0)
            else:
                # Non-core symptoms have 20% chance of being present
                symptom_vector.append(1 if np.random.random() < 0.2 else 0)
        
        data.append(symptom_vector)
        labels.append(disease)
    
    return pd.DataFrame(data, columns=symptoms), labels

# Train the model
def train_model():
    print("Creating synthetic dataset...")
    X, y = create_synthetic_dataset()
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    # Train Random Forest Classifier
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    # Save model and label encoder
    joblib.dump(model, 'models/disease_model.pkl')
    joblib.dump(label_encoder, 'models/label_encoder.pkl')
    joblib.dump(list(X.columns), 'models/symptom_list.pkl')
    
    print("\nModel saved successfully!")
    return model, label_encoder

if __name__ == "__main__":
    import os
    os.makedirs('models', exist_ok=True)
    train_model()