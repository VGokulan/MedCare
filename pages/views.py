from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from predictor import process_and_predict 
from .models import CustomUser, PatientAnalysis # Make sure to import PatientAnalysis
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.paginator import Paginator # Import Django's Paginator
from django.db.models import Q 
from django.core.cache import cache 



# --- Page Rendering Views ---

def home(request):
    return render(request, 'pages/home.html')

def login_page(request):
    return render(request, 'pages/login.html')

# VIEW 1: This function's only job is to DISPLAY the signup page.
def signup_page(request):
    return render(request, 'pages/signup.html')


# --- Authentication Logic ---

def user_signup(request):
    if request.method != "POST":
        # If someone tries to access this URL directly, just send them away.
        return redirect('signup_page')

    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    if password != confirm_password:
        messages.error(request, "Passwords do not match")
        return redirect('signup_page')

    if CustomUser.objects.filter(email=email).exists():
        messages.error(request, "Email already registered")
        return redirect('signup_page')

    # CORRECTED: Create the user with the standard fields first.
    user = CustomUser.objects.create_user(email=email, password=password)
    # Then, set the custom fields like first_name.
    user.first_name = full_name
    user.save()

    messages.success(request, "Account created successfully! Please log in.")
    return redirect('login_page')



def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # This will use your custom EmailBackend
        user = authenticate(request, username=email, password=password)
        
        # Check if the user was authenticated AND if they are NOT an admin
        if user is not None and not user.is_staff:
            login(request, user)
            return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid credentials or you are an admin.")
            return redirect("login_page")
    return redirect("login_page")


def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('admin_id') # From your admin form
        password = request.POST.get('password')

        # Use the SAME secure authentication system for everyone
        user = authenticate(request, username=email, password=password)

        # Check if the user was authenticated AND if they ARE an admin
        if user is not None and user.is_staff:
            login(request, user) # Use Django's secure login function
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or you are not an admin.')
            return redirect('login_page')
    return redirect('login_page')


# --- Dashboards (with Security) ---

@login_required # This decorator ensures only logged-in users can access this page
def user_dashboard(request):
    # We can add a check to make sure an admin doesn't land here by mistake
    if request.user.is_staff:
        return redirect('admin_dashboard')
        
    return render(request, "pages/user_dashboard.html")


@login_required
def admin_dashboard(request):
    """
    Displays the admin dashboard with caching, full-dataset filtering, and pagination.
    """
    if not request.user.is_staff:
        return redirect('user_dashboard')

    # --- Step 1: Get Filters and Create Cache Key ---
    search_query = request.GET.get('search', '')
    risk_tier_query = request.GET.get('risk_tier', '')
    age_range_query = request.GET.get('age_range', '') # New age filter
    page_number = request.GET.get('page', 1)
    
    cache_key = f"admin_dashboard_{search_query}_{risk_tier_query}_{age_range_query}_{page_number}"
    cached_context = cache.get(cache_key)

    if cached_context:
        print("--- CACHE HIT! Loading data from Redis. ---")
        return render(request, 'pages/admin_dashboard.html', cached_context)
    
    # --- Step 2: If No Cache, Query the FULL Database ---
    print("--- CACHE MISS! Querying PostgreSQL database. ---")
    
    # We start with the full list of patients, no [:150] limit.
    patient_list = PatientAnalysis.objects.all()

    # Apply filters from your function
    if search_query:
        search_filter = Q(desynpuf_id__icontains=search_query)
        if search_query.isnumeric():
            search_filter |= Q(age=search_query)
        patient_list = patient_list.filter(search_filter)
    
    if risk_tier_query:
        patient_list = patient_list.filter(risk_tier=risk_tier_query)
    
    # Add the age range filter
    if age_range_query:
        try:
            min_age, max_age = map(int, age_range_query.split('-'))
            patient_list = patient_list.filter(age__gte=min_age, age__lte=max_age)
        except ValueError:
            pass # Ignore invalid age range formats

    # --- Step 3: Paginate the FULL, Filtered List ---
    paginator = Paginator(patient_list, 10) # Django handles getting only 10 items
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_user': request.user,
        'filter_options': { 'risk_tiers': PatientAnalysis.RISK_TIER_CHOICES },
        'current_filters': { 
            'search': search_query, 
            'risk_tier': risk_tier_query,
            'age_range': age_range_query # Pass to template
        }
    }

    # --- Step 4: Save the Result to the Cache ---
    cache.set(cache_key, context, timeout=900) # Cache for 15 minutes

    return render(request, 'pages/admin_dashboard.html', context)

    # try:
       

    # except Exception as e:
    #     return render(request, 'pages/error.html', {'error': str(e)})

@login_required
def upload_data(request):
    """
    Handles displaying the upload form and processing the submitted data.
    """
    if not request.user.is_staff:
        # Security check
        return redirect('user_dashboard')

    if request.method == 'POST':
        # This is where you would connect to your ML model's prediction function.
        # For now, we'll simulate a successful response.
        simulated_results = {
            "risk_tier": 2,
            "risk_tier_label": "High Risk",
            "risk_30d_hospitalization": 0.15,
            "risk_60d_hospitalization": 0.25,
            "risk_90d_hospitalization": 0.35,
            "mortality_risk": 0.10,
            # ... other result fields
        }
        return JsonResponse(simulated_results)

    # For a GET request, just render the page.
    context = {'user': request.user}
    return render(request, 'pages/upload.html', context)


def get_patient_list(search='', risk_level='', status='', age_range=''):
    patients = PatientAnalysis.objects.all()

    # 🔍 Search by Member ID
    if search:
        patients = patients.filter(desynpuf_id__icontains=search)

    # 🎯 Filter by risk tier (fix field name)
    if risk_level:
        patients = patients.filter(risk_tier_label=risk_level)

    # ⚡ Filter by status (only if PatientAnalysis actually has a `status` field)
    if status and hasattr(PatientAnalysis, 'status'):
        patients = patients.filter(status=status)

    # 👴 Filter by age range
    if age_range:
        try:
            min_age, max_age = map(int, age_range.split('-'))
            patients = patients.filter(age__gte=min_age, age__lte=max_age)
        except ValueError:
            pass

    return patients


def get_patient_filters():
    filters = {
        "risk_levels": PatientAnalysis.objects.values_list("risk_tier_label", flat=True).distinct(),
        "age_ranges": ["0-18", "19-35", "36-60", "60-100"],
    }

    # Add status filter only if model has that field
    if hasattr(PatientAnalysis, 'status'):
        filters["statuses"] = PatientAnalysis.objects.values_list("status", flat=True).distinct()
    else:
        filters["statuses"] = []

    return filters


# --- A SINGLE, UNIFIED LOGOUT ---

def user_logout(request):
    """Logs out both users and admins."""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("home")

@login_required
def upload_data(request):
    """
    Handles displaying the upload form (GET) and processing
    the ML prediction (POST).
    """
    if not request.user.is_staff:
        return redirect('user_dashboard')

    if request.method == 'POST':
        try:
            # Pass the form data (request.POST) directly to your processing function
            results = process_and_predict(request.POST)
            # Return the prediction results as a JSON response to the JavaScript
            return JsonResponse(results)
        except Exception as e:
            # If the predictor script fails, send a detailed error back as JSON
            return JsonResponse({'error': f"An error occurred during prediction: {str(e)}"}, status=500)

    # For a GET request, just render the page with the empty form
    context = {'user': request.user}
    return render(request, 'pages/upload.html', context)


# --- Contact Form View ---

def contact_submission(request):
    """
    Handles the submission of the contact form from the home page.
    This is the final, production-ready version.
    """
    if request.method == 'POST':
        # Get the form data from the POST request
        name = request.POST.get('contact_name')
        email = request.POST.get('contact_email')
        company = request.POST.get('contact_company', 'Not Provided')
        message = request.POST.get('contact_message')

        # Basic validation to ensure required fields are not empty
        if not name or not email or not message:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('/#contact')

        # Construct the email message
        subject = f'New Contact Form Message from {name}'
        email_body = f"""
        You have received a new message from your website's contact form:

        Name: {name}
        Email: {email}
        Company: {company}

        Message:
        {message}
        """
        try:
            # Send the email using the settings from settings.py
            send_mail(
                subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                ['ragulroshan45@gmail.com'], # Your receiving email address
                fail_silently=False,
            )
            # Provide a success message to the user on the webpage
            messages.success(request, 'Thank you! Your message has been sent successfully.')
        except Exception:
            # If the email fails for any reason, provide a generic error message.
            # We don't show the specific error to the user for security reasons.
            messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')

        # Redirect back to the home page, specifically to the contact section
        return redirect('/#contact')

    # If a user tries to access this URL with a GET request, just send them home.
    return redirect('home')
