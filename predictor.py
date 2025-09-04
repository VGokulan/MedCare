import pickle
import pandas as pd
import numpy as np
# We now import the Django model directly
from pages.models import PatientAnalysis

class Predictor:
    def __init__(self):
        self.pipeline = None
        self.models = None
        self.feature_columns = []
        self.load_models()
    
    def load_models(self):
        try:
            # Make sure these .pkl files are in your project's root directory
            with open('preprocessing_pipeline.pkl', 'rb') as f:
                self.pipeline = pickle.load(f)
            
            with open('risk_models.pkl', 'rb') as f:
                models_data = pickle.load(f)
                self.models = models_data['models']
                self.feature_columns = models_data['feature_columns']
        except FileNotFoundError:
            print("WARNING: Model files (preprocessing_pipeline.pkl, risk_models.pkl) not found. Prediction will not work.")
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def predict(self, input_data):
        if not self.pipeline or not self.models:
            raise Exception("Models are not loaded. Cannot make predictions.")
        
        # Ensure all required features are present, defaulting to 0 if not
        for feature in self.feature_columns:
            if feature not in input_data:
                input_data[feature] = 0
        
        input_df = pd.DataFrame([input_data])
        X_input = input_df[self.feature_columns]
        X_scaled = self.pipeline.transform(X_input)
        
        predictions = {}
        for model_name, model in self.models.items():
            prob = model.predict_proba(X_scaled)[0, 1]
            predictions[model_name] = prob
        
        return predictions

# Initialize a single predictor instance to be used by the app
predictor = Predictor()

def store_prediction_in_db(input_data, results):
    """
    Saves the prediction results to the database using Django's ORM.
    This is the secure and maintainable way to handle database operations.
    """
    try:
        # Combine the input data and the prediction results
        combined_data = {**input_data, **results}

        # Create a new PatientAnalysis record using the model
        # The **combined_data dictionary is unpacked to fill the model fields
        record = PatientAnalysis(**combined_data)
        
        # Save the new record to the PostgreSQL database
        record.save()
        
        print("Prediction stored successfully in patient_analysis table.")
        return True
    except Exception as e:
        print(f"Error storing prediction in DB: {e}")
        return False


def process_and_predict(form_data):
    """
    The main function that orchestrates the prediction process.
    """
    # Convert form data from strings to numbers
    processed_data = {}
    for key, value in form_data.items():
        if key in ['DESYNPUF_ID', 'name', 'risk_tier_label', 'care_intervention']:
            processed_data[key] = value # Keep these as strings
        else:
            try:
                processed_data[key] = float(value) if '.' in value else int(value)
            except (ValueError, TypeError):
                processed_data[key] = value

    # Ensure all checkbox condition fields are present (set to 0 if not checked)
    condition_fields = [
        'SP_CHF', 'SP_DIABETES', 'SP_CHRNKIDN', 'SP_CNCR', 'SP_COPD', 
        'SP_DEPRESSN', 'SP_ISCHMCHT', 'SP_STRKETIA', 'SP_ALZHDMTA', 
        'SP_OSTEOPRS', 'SP_RA_OA'
    ]
    for field in condition_fields:
        if field not in processed_data:
            processed_data[field] = 0

    # Get predictions from the ML model
    predictions = predictor.predict(processed_data)
    
    # Calculate risk tier (simplified logic)
    avg_prob = np.mean(list(predictions.values()))
    if avg_prob >= 0.7: risk_tier, risk_label = 1, "Critical"
    elif avg_prob >= 0.5: risk_tier, risk_label = 2, "High Risk"
    elif avg_prob >= 0.3: risk_tier, risk_label = 3, "Medium Risk"
    elif avg_prob >= 0.1: risk_tier, risk_label = 4, "Low Risk"
    else: risk_tier, risk_label = 5, "Healthy"

    # Prepare final results dictionary
    results = {
        'risk_tier': risk_tier,
        'risk_tier_label': risk_label,
        'risk_30d_hospitalization': round(predictions.get('hospitalization_30d', 0), 4),
        'risk_60d_hospitalization': round(predictions.get('hospitalization_60d', 0), 4),
        'risk_90d_hospitalization': round(predictions.get('hospitalization_90d', 0), 4),
        'mortality_risk': round(predictions.get('mortality', 0), 4),
        'care_intervention': "Enhanced Monitoring",
        'annual_intervention_cost': 400,
        'cost_savings': 1200,
        'prevented_hospitalizations': 0.15
    }
    
    # Store the results in the database
    store_prediction_in_db(processed_data, results)
    
    return results
