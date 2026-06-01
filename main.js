// Load symptoms on predict page
if (window.location.pathname === '/predict') {
    loadSymptoms();
    setupPredictionForm();
}

// Load symptoms list
async function loadSymptoms() {
    try {
        const response = await fetch('/api/symptoms');
        const data = await response.json();
        
        const symptomsGrid = document.getElementById('symptomsGrid');
        if (symptomsGrid) {
            symptomsGrid.innerHTML = data.symptoms.map(symptom => `
                <label class="symptom-checkbox">
                    <input type="checkbox" value="${symptom}">
                    <span>${symptom.replace(/_/g, ' ').toUpperCase()}</span>
                </label>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading symptoms:', error);
    }
}

// Setup prediction form submission
function setupPredictionForm() {
    const form = document.getElementById('predictionForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get selected symptoms
        const checkboxes = document.querySelectorAll('#symptomsGrid input[type="checkbox"]:checked');
        const selectedSymptoms = Array.from(checkboxes).map(cb => cb.value);
        
        if (selectedSymptoms.length === 0) {
            alert('Please select at least one symptom');
            return;
        }
        
        // Get patient details
        const patientData = {
            patient_name: document.getElementById('patientName').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            contact: document.getElementById('contact').value,
            symptoms: selectedSymptoms
        };
        
        // Show loading state
        const submitBtn = form.querySelector('.submit-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Predicting...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(patientData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                displayPredictionResult(result);
                form.reset();
                // Uncheck all symptoms
                document.querySelectorAll('#symptomsGrid input[type="checkbox"]').forEach(cb => cb.checked = false);
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            alert('Error making prediction: ' + error.message);
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
}

// Display prediction result
function displayPredictionResult(result) {
    const resultDiv = document.getElementById('result');
    const predictionResult = document.getElementById('predictionResult');
    
    predictionResult.innerHTML = `
        <h3>${result.predicted_disease}</h3>
        <p>Confidence Score: ${result.confidence}%</p>
        <p>Patient ID: ${result.patient_id}</p>
        <small>Please consult a doctor for proper diagnosis</small>
    `;
    
    resultDiv.style.display = 'block';
    
    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// Load records on records page
if (window.location.pathname === '/records') {
    loadRecords();
    setupSearch();
}

// Load prediction records
async function loadRecords() {
    try {
        const response = await fetch('/api/records');
        const data = await response.json();
        
        const recordsList = document.getElementById('recordsList');
        
        if (data.records.length === 0) {
            recordsList.innerHTML = '<p style="text-align: center;">No records found</p>';
            return;
        }
        
        recordsList.innerHTML = data.records.map(record => `
            <div class="record-card" data-name="${record.name.toLowerCase()}" data-disease="${record.predicted_disease.toLowerCase()}">
                <div class="record-header">
                    <span class="patient-name">${record.name}</span>
                    <span class="prediction-date">${record.prediction_date}</span>
                </div>
                <div class="record-details">
                    <p><strong>Age:</strong> ${record.age} | <strong>Gender:</strong> ${record.gender}</p>
                    <p><strong>Predicted Disease:</strong> <span class="disease-name">${record.predicted_disease}</span></p>
                    <p><strong>Confidence:</strong> <span class="confidence">${record.confidence_score}%</span></p>
                    <p><strong>Symptoms:</strong> <span class="symptoms-list">${record.symptoms_list.join(', ')}</span></p>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading records:', error);
        document.getElementById('recordsList').innerHTML = '<p style="text-align: center; color: red;">Error loading records</p>';
    }
}

// Setup search functionality
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const recordCards = document.querySelectorAll('.record-card');
        
        recordCards.forEach(card => {
            const name = card.getAttribute('data-name');
            const disease = card.getAttribute('data-disease');
            
            if (name.includes(searchTerm) || disease.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}