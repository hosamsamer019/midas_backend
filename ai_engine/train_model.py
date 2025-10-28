import os
import sys
import django
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from results.models import TestResult
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic

def prepare_data():
    """Prepare data for training from database"""
    # Get all test results with related data
    results = TestResult.objects.select_related('sample__bacteria', 'antibiotic').all()

    data = []
    for result in results:
        data.append({
            'bacteria_name': result.sample.bacteria.name,
            'bacteria_type': result.sample.bacteria.bacteria_type,
            'gram_stain': result.sample.bacteria.gram_stain,
            'antibiotic_name': result.antibiotic.name,
            'category': result.antibiotic.category,
            'mechanism': result.antibiotic.mechanism,
            'sensitivity': result.sensitivity,
            'zone_diameter': result.zone_diameter or 0,
            'department': result.sample.department,
            'hospital': result.sample.hospital
        })

    df = pd.DataFrame(data)

    if df.empty:
        print("No data available for training")
        return None, None, None

    # Encode categorical variables
    le_bacteria = LabelEncoder()
    le_antibiotics = LabelEncoder()
    le_category = LabelEncoder()
    le_mechanism = LabelEncoder()
    le_department = LabelEncoder()
    le_hospital = LabelEncoder()
    le_sensitivity = LabelEncoder()

    df['bacteria_encoded'] = le_bacteria.fit_transform(df['bacteria_name'])
    df['antibiotic_encoded'] = le_antibiotics.fit_transform(df['antibiotic_name'])
    df['category_encoded'] = le_category.fit_transform(df['category'])
    df['mechanism_encoded'] = le_mechanism.fit_transform(df['mechanism'])
    df['department_encoded'] = le_department.fit_transform(df['department'])
    df['hospital_encoded'] = le_hospital.fit_transform(df['hospital'])
    df['sensitivity_encoded'] = le_sensitivity.fit_transform(df['sensitivity'])

    # Features for prediction
    X = df[['bacteria_encoded', 'category_encoded', 'mechanism_encoded',
            'zone_diameter', 'department_encoded', 'hospital_encoded']]

    # Target: sensitivity (0=intermediate, 1=resistant, 2=sensitive)
    y = df['sensitivity_encoded']

    return X, y, {
        'bacteria_encoder': le_bacteria,
        'antibiotics_encoder': le_antibiotics,
        'category_encoder': le_category,
        'mechanism_encoder': le_mechanism,
        'department_encoder': le_department,
        'hospital_encoder': le_hospital,
        'sensitivity_encoder': le_sensitivity
    }

def train_model():
    """Train the Random Forest model"""
    print("Preparing data for training...")
    X, y, encoders = prepare_data()

    if len(X) == 0:
        print("No data available for training")
        return None, None

    print(f"Training on {len(X)} samples...")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Model Accuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    # Get unique classes in y_test to match target_names
    unique_classes = np.unique(np.concatenate([y_test, y]))
    target_names = encoders['sensitivity_encoder'].inverse_transform(unique_classes)
    print(classification_report(y_test, y_pred, target_names=target_names, labels=unique_classes))

    return model, encoders

def save_model(model, encoders, model_path='ai_engine/model.pkl', encoders_path='ai_engine/encoders.pkl'):
    """Save trained model and encoders"""
    os.makedirs('ai_engine', exist_ok=True)

    joblib.dump(model, model_path)
    joblib.dump(encoders, encoders_path)

    print(f"Model saved to {model_path}")
    print(f"Encoders saved to {encoders_path}")

def load_model(model_path='ai_engine/model.pkl', encoders_path='ai_engine/encoders.pkl'):
    """Load trained model and encoders"""
    try:
        model = joblib.load(model_path)
        encoders = joblib.load(encoders_path)
        return model, encoders
    except FileNotFoundError:
        print("Model files not found. Please train the model first.")
        return None, None

def predict_antibiotic(bacteria_name, encoders, model, top_n=3):
    """Predict antibiotic effectiveness for a given bacteria"""
    try:
        bacteria_encoded = encoders['bacteria_encoder'].transform([bacteria_name])[0]
    except ValueError:
        return {"error": f"Bacteria '{bacteria_name}' not found in training data"}

    # Get all antibiotics
    antibiotics = Antibiotic.objects.all()

    predictions = []
    for antibiotic in antibiotics:
        try:
            category_encoded = encoders['category_encoder'].transform([antibiotic.category])[0]
            mechanism_encoded = encoders['mechanism_encoder'].transform([antibiotic.mechanism])[0]
        except ValueError:
            continue  # Skip if category/mechanism not in training data

        # Create feature vector (using default values for department/hospital/zone)
        features = np.array([[bacteria_encoded, category_encoded, mechanism_encoded, 20, 0, 0]])

        # Get prediction probabilities
        proba = model.predict_proba(features)[0]

        # Get the class with highest probability
        predicted_class_idx = np.argmax(proba)
        confidence = proba[predicted_class_idx]

        sensitivity_label = encoders['sensitivity_encoder'].inverse_transform([predicted_class_idx])[0]

        predictions.append({
            'antibiotic': antibiotic.name,
            'predicted_sensitivity': sensitivity_label,
            'confidence': float(confidence),
            'category': antibiotic.category,
            'mechanism': antibiotic.mechanism
        })

    # Sort by confidence (higher is better for sensitive predictions)
    sensitive_predictions = [p for p in predictions if p['predicted_sensitivity'] == 'sensitive']
    sensitive_predictions.sort(key=lambda x: x['confidence'], reverse=True)

    return {
        'bacteria': bacteria_name,
        'recommendations': sensitive_predictions[:top_n],
        'total_antibiotics': len(predictions)
    }

if __name__ == "__main__":
    print("Training AI Model for Antibiotic Recommendations...")
    model, encoders = train_model()

    if model:
        save_model(model, encoders)
        print("Model training completed successfully!")
    else:
        print("Model training failed!")
