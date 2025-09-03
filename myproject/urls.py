"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
# Import Django's built-in authentication views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- PASSWORD RESET URLS ---
    # We are now explicitly defining each password reset URL so we can tell
    # it which custom template to use. This overrides the defaults.

    path(
        'accounts/password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='pages/password_reset_form.html'  # Tell Django to use OUR template
        ),
        name='password_reset'
    ),
    path(
        'accounts/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='pages/password_reset_done.html' # Tell Django to use OUR template
        ),
        name='password_reset_done'
    ),
    path(
        'accounts/password_reset_confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='pages/password_reset_confirm.html' # Tell Django to use OUR template
        ),
        name='password_reset_confirm'
    ),
    path(
        'accounts/password_reset_complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='pages/password_reset_complete.html' # Tell Django to use OUR template
        ),
        name='password_reset_complete'
    ),
    
    # --- YOUR APP's URLS ---
    # This includes all the other URLs from your `pages` app (login, signup, dashboards, etc.)
    path('', include('pages.urls')),
]