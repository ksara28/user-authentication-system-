"""
URL patterns for accounts (authentication) app.

Includes routes for:
- Signup and email verification
- Login and logout
- Password reset
- User and admin dashboards
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('verify-email-pending/<str:uidb64>/', views.verify_email_pending, name='verify_email_pending'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('verify-email-reminder/', views.verify_email_reminder, name='verify_email_reminder'),
    
    # Login and Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
