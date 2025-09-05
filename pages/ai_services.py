import google.generativeai as genai
from django.conf import settings
from .models import Patient, PatientAnalysis
import json

# --- Configuration (Done once when the server starts) ---
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
except AttributeError:
    print("ERROR: GOOGLE_API_KEY not found in settings.py. AI features will not work.")

# --- System Instructions (Copied from your script) ---
CHATBOT_SYSTEM_INSTRUCTION = """You are an AI assistant specialized in patient risk analysis and intervention planning...""" # (Keep your full prompt here)
SUMMARY_SYSTEM_INSTRUCTION = """You are a medical AI assistant. Based on the complete patient data provided, generate a concise clinical summary...""" # (Keep your full prompt here)

# --- Helper function to format Django model data for the AI ---
def format_patient_context(patient: PatientAnalysis):
    """Formats the PatientAnalysis model instance into a string for the AI prompt."""
    if not patient:
        return ""
    
    # Get all field names and their values from the model instance
    patient_data = {f.name: getattr(patient, f.name) for f in patient._meta.get_fields() if not f.is_relation}
    
    details = ["**Complete Patient Record:**"]
    for key, value in patient_data.items():
        clean_key = key.replace('_', ' ').title()
        display_value = value if value is not None else "N/A"
        details.append(f"- **{clean_key}:** {display_value}")
        
    return "\n".join(details)

# --- Main Functions ---

def get_ai_summary(patient: PatientAnalysis):
    """Generates a clinical summary for a given patient model instance."""
    try:
        patient_context = format_patient_context(patient)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SUMMARY_SYSTEM_INSTRUCTION
        )
        prompt = f"Generate the summary for the following patient:\n{patient_context}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return "Could not generate AI summary due to a server error."

def get_chatbot_response(patient: PatientAnalysis, user_message: str, chat_history: list = None):
    """Gets a response from the AI chatbot for a given patient and message."""
    try:
        patient_context = format_patient_context(patient)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=CHATBOT_SYSTEM_INSTRUCTION + "\n\n" + patient_context
        )
        
        # In a stateless web app, we start a new chat for each request.
        # A more advanced version could store history in the user's session.
        chat = model.start_chat(history=chat_history or [])
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        return f"Error getting AI response: {str(e)}"
