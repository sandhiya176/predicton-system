CREATE DATABASE IF NOT EXISTS disease_prediction;
USE disease_prediction;

-- Patients table
CREATE TABLE patients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    contact VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table
CREATE TABLE predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    symptom_1 VARCHAR(100),
    symptom_2 VARCHAR(100),
    symptom_3 VARCHAR(100),
    symptom_4 VARCHAR(100),
    symptom_5 VARCHAR(100),
    predicted_disease VARCHAR(100),
    confidence_score FLOAT,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Sample data for symptoms (20 common symptoms)
INSERT INTO patients (name, age, gender, contact) VALUES 
('John Doe', 35, 'Male', '1234567890'),
('Jane Smith', 28, 'Female', '0987654321');