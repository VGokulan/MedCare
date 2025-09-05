import pickle
import pandas as pd
import numpy as np
from pages.models import Patient, PatientAnalysis

class Predictor:
    """
    A class to load the ML models and preprocessing pipeline once,
    and then use them to make predictions.
    """
    def __init__(self):
        self.pipeline = None
        self.models = None
        self.feature_columns = []
        self.load_models()
    
    def load_models(self):
        try:
            with open('preprocessing_pipeline.pkl', 'rb') as f:
                self.pipeline = pickle.load(f)
            with open('risk_models.pkl', 'rb') as f:
                models_data = pickle.load(f)
                self.models = models_data['models']
                self.feature_columns = models_data['feature_columns']
        except FileNotFoundError:
            print("WARNING: Model files not found. Prediction will not work.")
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def predict(self, input_data):
        if not self.pipeline or not self.models:
            raise Exception("Models are not loaded.")
        
        temp_input = {k.lower(): v for k, v in input_data.items()}
        for feature in self.feature_columns:
            if feature not in temp_input:
                temp_input[feature] = 0
                
        input_df = pd.DataFrame([temp_input])
        X_input = input_df[self.feature_columns]
        X_scaled = self.pipeline.transform(X_input)
        
        predictions = {}
        for model_name, model in self.models.items():
            prob = model.predict_proba(X_scaled)[0, 1]
            predictions[f'risk_{model_name}'] = prob
            
        return predictions

predictor = Predictor()

def store_prediction_results(all_data):
    """
    Saves or updates prediction results using Django's ORM.
    This version filters data to match the model and expects integers for boolean fields.
    """
    try:
        patient_id = str(all_data.get('desynpuf_id'))
        patient_name = all_data.get('name')

        if patient_name and patient_id:
            Patient.objects.update_or_create(
                desynpuf_id=patient_id,
                defaults={'name': patient_name}
            )

        valid_field_names = {f.name for f in PatientAnalysis._meta.get_fields()}
        data_to_save = {key: value for key, value in all_data.items() if key in valid_field_names}
        
        # NOTE: Boolean-to-integer conversion is no longer needed here,
        # as the model and incoming data now both use integers (0 or 1).

        if 'desynpuf_id' in data_to_save:
            analysis_id = data_to_save.pop('desynpuf_id')
            PatientAnalysis.objects.update_or_create(
                desynpuf_id=analysis_id,
                defaults=data_to_save
            )
        
        print("Prediction stored successfully")
    except Exception as e:
        print(f"Error storing prediction: {e}")
        raise

def process_and_predict(form_data):
    """
    The main function that orchestrates the prediction process.
    """
    processed_data = {}
    # This loop correctly converts form values ('1', '0', etc.) into integers, matching the model.
    for key, value in form_data.items():
        if key.upper().startswith('SP_') or key in ['gender_male', 'race_white', 'race_black', 'prior_hospitalization']:
            processed_data[key.lower()] = int(value)
        elif key in ['desynpuf_id', 'name', 'csrfmiddlewaretoken']:
            processed_data[key.lower()] = value
        else:
            try:
                processed_data[key.lower()] = float(value) if '.' in value else int(value)
            except (ValueError, TypeError):
                processed_data[key.lower()] = value

    # Fill in any missing checkbox values with 0
    condition_fields = ['sp_chf', 'sp_diabetes', 'sp_chrnkidn', 'sp_cncr', 'sp_copd', 'sp_depressn', 'sp_ischmcht', 'sp_strketia', 'sp_alzhdmta', 'sp_osteoprs', 'sp_ra_oa']
    for field in condition_fields:
        if field not in processed_data:
            processed_data[field] = 0
            
    predictions = predictor.predict(processed_data)

    primary_risk_score = predictions.get('risk_30d_hospitalization') or 0
    if primary_risk_score >= 0.85: risk_tier = '5'
    elif primary_risk_score >= 0.65: risk_tier = '4'
    elif primary_risk_score >= 0.40: risk_tier = '3'
    elif primary_risk_score >= 0.15: risk_tier = '2'
    else: risk_tier = '1'

    tier_info = {
        '1': {'label': 'Low Risk', 'intervention': 'Preventive Care', 'cost': 200, 'rate': 0.02},
        '2': {'label': 'Low-Moderate Risk', 'intervention': 'Enhanced Wellness', 'cost': 300, 'rate': 0.05},
        '3': {'label': 'Moderate Risk', 'intervention': 'Care Coordination', 'cost': 600, 'rate': 0.15},
        '4': {'label': 'High Risk', 'intervention': 'Case Management', 'cost': 800, 'rate': 0.25},
        '5': {'label': 'Critical Risk', 'intervention': 'Intensive Management', 'cost': 1000, 'rate': 0.35}
    }
    
    avg_preventable_cost = 10000
    prevention_rate = tier_info[risk_tier]['rate']
    prevented_hospitalizations = primary_risk_score * prevention_rate
    cost_savings = prevented_hospitalizations * avg_preventable_cost

    final_results = {
        **processed_data,
        **predictions,
        'risk_tier': risk_tier,
        'risk_tier_label': tier_info[risk_tier]['label'],
        'care_intervention': tier_info[risk_tier]['intervention'],
        'annual_intervention_cost': tier_info[risk_tier]['cost'],
        'prevented_hospitalizations': prevented_hospitalizations,
        'cost_savings': cost_savings,
    }

    store_prediction_results(final_results)
    
    # Return a clean dictionary to the frontend for display
    return {
        'risk_tier': risk_tier,
        'risk_tier_label': tier_info[risk_tier]['label'],
        'risk_30d_hospitalization': primary_risk_score,
        'risk_60d_hospitalization': predictions.get('risk_60d_hospitalization'),
        'risk_90d_hospitalization': predictions.get('risk_90d_hospitalization'),
        'mortality_risk': predictions.get('risk_mortality'),
        'care_intervention': tier_info[risk_tier]['intervention'],
    }

