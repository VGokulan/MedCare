from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Login page (renders the HTML with both forms)
    path('login/', views.login_page, name='login_page'),
    path('signup/', views.signup_page, name='signup_page'),
    path('upload/', views.upload_data, name='upload_data'),

    # Form POST handlers
    path('user_signup/', views.user_signup, name='user_signup'),
    path('user_login/', views.user_login, name='user_login'),

    path('patient/<str:patient_id>/', views.patient_detail, name='patient_detail'),

    path('api/ai-summary/<str:patient_id>/', views.get_ai_summary_view, name='ai_summary'),
    path('api/chatbot/', views.chatbot_view, name='chatbot'),

    path('admin_login/', views.admin_login, name='admin_login'),
    path('contact-submission/', views.contact_submission, name='contact_submission'),


    # Logout
    path('logout/', views.user_logout, name='logout'),


    # Dashboards
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('upload/', views.upload_data, name='upload_data'),

    
]
