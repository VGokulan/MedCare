from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, PatientAnalysis # Make sure to import PatientAnalysis
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse



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
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('user_dashboard')

    try:
        search = request.GET.get('search', '')
        risk_level = request.GET.get('risk_level', '')
        status = request.GET.get('status', '')
        age_range = request.GET.get('age_range', '')

        patients = get_patient_list(search, risk_level, status, age_range)
        filter_options = get_patient_filters()

        return render(request, 'pages/admin_dashboard.html', {
    'patients': patients,
    'filter_options': filter_options,
    'current_filters': {
        'search': search,
        'risk_level': risk_level,
        'status': status,
        'age_range': age_range
    }
})

    except Exception as e:
        return render(request, 'pages/error.html', {'error': str(e)})




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
