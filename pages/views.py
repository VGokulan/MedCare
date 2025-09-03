from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, PatientAnalysis # Make sure to import PatientAnalysis
from django.conf import settings
from django.core.mail import send_mail

# --- Page Rendering Views ---

def home(request):
    return render(request, 'pages/home.html')

def login_page(request):
    return render(request, 'pages/login.html')

def signup_page(request):
    return render(request, 'pages/signup.html')

# --- Authentication Logic ---

def user_signup(request):
    if request.method == "POST":
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

        # Create the user using Django's secure method
        user = CustomUser.objects.create_user(email=email, password=password)
        # Set the first_name after creation
        user.first_name = full_name
        user.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login_page')
    return redirect('signup_page')


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


@login_required # This decorator ensures only logged-in users can access this page
def admin_dashboard(request):
    # This check is a security layer. If a regular user tries to access this URL,
    # they will be redirected away.
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('user_dashboard')

    # Fetch all patient data from the database
    all_patients_analysis = PatientAnalysis.objects.all()
    
    context = {
        'patients': all_patients_analysis,
        'current_user': request.user
    }
    return render(request, "pages/admin_dashboard.html", context)


# --- A SINGLE, UNIFIED LOGOUT ---

def user_logout(request):
    """Logs out both users and admins."""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("home")


# --- Contact Form View ---

def contact_submission(request):
    if request.method == 'POST':
        # ... (your complete, working contact_submission code)
        name = request.POST.get('contact_name')
        email = request.POST.get('contact_email')
        company = request.POST.get('contact_company', 'Not Provided')
        message = request.POST.get('contact_message')
        if not name or not email or not message:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('/#contact')
        subject = f'New Contact Form Message from {name}'
        email_body = f"Name: {name}\nEmail: {email}\nCompany: {company}\n\nMessage:\n{message}"
        try:
            send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, ['ragulroshan45@gmail.com'], fail_silently=False)
            messages.success(request, 'Thank you! Your message has been sent successfully.')
        except Exception:
            messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')
        return redirect('/#contact')
    return redirect('home')
