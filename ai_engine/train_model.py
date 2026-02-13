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

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def predict_antibiotic(bacteria_name, encoders=None, model=None, top_n=None):
    """Predict antibiotic effectiveness for a given bacteria using database statistics"""
    try:
        # Get the bacteria object
        bacteria = Bacteria.objects.get(name=bacteria_name)
    except Bacteria.DoesNotExist:
        return {"error": f"Bacteria '{bacteria_name}' not found in database"}

    # Get all antibiotics
    antibiotics = Antibiotic.objects.all()

    recommendations = []
    for antibiotic in antibiotics:
        # Query database for actual sensitivity statistics
        total_tests = TestResult.objects.filter(
            sample__bacteria=bacteria,
            antibiotic=antibiotic
        ).count()

        sensitive_count = TestResult.objects.filter(
            sample__bacteria=bacteria,
            antibiotic=antibiotic,
            sensitivity__iexact='sensitive'
        ).count()

        # Calculate effectiveness percentage (0 if no tests)
        effectiveness = (sensitive_count / total_tests) * 100 if total_tests > 0 else 0

        recommendations.append({
            'antibiotic': antibiotic.name,
            'effectiveness': round(effectiveness, 2),
            'total_tests': total_tests,
            'sensitive_cases': sensitive_count,
            'category': antibiotic.category,
            'mechanism': antibiotic.mechanism
        })

    # Sort by effectiveness (higher is better)
    recommendations.sort(key=lambda x: x['effectiveness'], reverse=True)

    # Return all antibiotics if top_n is None, otherwise limit to top_n
    result_recommendations = recommendations if top_n is None else recommendations[:top_n]

    return {
        'bacteria': bacteria_name,
        'recommendations': result_recommendations,
        'total_antibiotics': len(antibiotics),
        'tested_antibiotics': len([r for r in recommendations if r['total_tests'] > 0])
    }

if __name__ == "__main__":
    print("Training AI Model for Antibiotic Recommendations...")
    model, encoders = train_model()

    if model:
        save_model(model, encoders)
        print("Model training completed successfully!")
    else:
        print("Model training failed!")
