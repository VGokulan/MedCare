from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Login page (renders the HTML with both forms)
    path('login/', views.login_page, name='login_page'),

    # Form POST handlers
    path('user_login/', views.user_login, name='user_login'),
    path('admin_login/', views.admin_login, name='admin_login'),

    # Signup
    path('signup/', views.signup_page, name='signup_page'),

    # Logout
    path('logout/', views.user_logout, name='logout'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),


    # Dashboards
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
