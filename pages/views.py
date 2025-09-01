from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from .models import CustomUser
from pages.models import Admin
from django.contrib.auth import get_user_model



def home(request):
    return render(request, 'pages/home.html')

def login_page(request):
    return render(request, 'pages/login.html')

User = get_user_model()   # ✅ This ensures we always use CustomUser

def signup_page(request):
    if request.method == "POST":
        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup_page')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('signup_page')

        # ✅ Don’t pass username, only email + full_name + password
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name
        )
        user.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login_page')

    return render(request, 'pages/signup.html')
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("login_page")

    return redirect("login_page")

def user_dashboard(request):
    # Check if user is logged in
    if request.user.is_authenticated:
        return render(request, "pages/user_dashboard.html")
    else:
        messages.error(request, "You must login to access this page.")
        return redirect("login_page")


def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            admin_user = Admin.objects.get(email=email)
            if check_password(password, admin_user.password):
                request.session['admin_logged_in'] = True
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('login_page')
        except Admin.DoesNotExist:
            messages.error(request, 'Invalid credentials')
            return redirect('login_page')

    return render(request, 'pages/login.html') # ⚠️ use a separate template

def admin_dashboard(request):
    # Check if admin is logged in
    if request.session.get('admin_logged_in'):
        return render(request, "pages/admin_dashboard.html")
    else:
        messages.error(request, "You must login as admin to access this page.")
        return redirect("login_page")


def user_logout(request):
    logout(request)
    return redirect("login_page")

def admin_logout(request):
    request.session.pop('admin_logged_in', None)
    return redirect('login_page')



