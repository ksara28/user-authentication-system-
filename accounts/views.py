"""
Authentication views handling signup, email verification, login, logout, and password reset.

Security features:
- CSRF protection (automatic with Django)
- Secure session management with 15-minute timeout
- Email verification required before login
- Token-based password reset
- Role-Based Access Control (RBAC)
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from functools import wraps
import logging

from .forms import SignupForm, LoginForm, PasswordResetRequestForm, PasswordResetForm
from .models import UserProfile
from .tokens import (
    email_verification_token,
    password_reset_token,
    encode_uid,
    decode_uid
)

logger = logging.getLogger(__name__)


# ============================================================================
# RBAC DECORATORS - Role-Based Access Control
# ============================================================================

def role_required(required_role):
    """
    Decorator to restrict views based on user role.
    
    Usage:
        @role_required('admin')
        def admin_dashboard(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login first.')
                return redirect('accounts:login')
            
            try:
                user_profile = request.user.profile
                if user_profile.role != required_role:
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect('accounts:dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found.')
                return redirect('accounts:logout')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to restrict view to admins only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first.')
            return redirect('accounts:login')
        
        try:
            if not request.user.profile.is_admin():
                messages.error(request, 'You do not have admin access.')
                return redirect('accounts:dashboard')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('accounts:logout')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def email_verified_required(view_func):
    """Decorator to ensure user has verified email before accessing view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first.')
            return redirect('accounts:login')
        
        try:
            if not request.user.profile.is_email_verified():
                messages.warning(request, 'Please verify your email first.')
                return redirect('accounts:verify_email_reminder')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found.')
            return redirect('accounts:logout')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def signup(request):
    """
    User registration view.
    
    Flow:
    1. User submits email and password
    2. Form validates email uniqueness and password strength
    3. User created with is_active=False (inactive until email verified)
    4. Verification email sent with token link
    5. User redirected to verification pending page
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                
                # Create inactive user (will be activated after email verification)
                user = User.objects.create_user(
                    username=email,  # Use email as username
                    email=email,
                    password=password,
                    is_active=False  # CRITICAL: User cannot login until email verified
                )
                
                # Generate email verification token
                uid = encode_uid(user.pk)
                token = email_verification_token.make_token(user)
                
                # Save token to user profile
                user_profile = UserProfile.objects.create(
                    user=user,
                    email_verification_token=token,
                    email_verification_created=now()
                )
                
                # Send verification email
                verification_url = request.build_absolute_uri(
                    reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
                )
                
                email_subject = 'Verify Your Email - Authentication System'
                email_body = f"""
Hello {email},

Thank you for registering! To activate your account, please verify your email by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not register for this account, please ignore this email.

Best regards,
Authentication System Team
"""
                
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(
                    request,
                    'Registration successful! Check your email to verify your account.'
                )
                return redirect('accounts:verify_email_pending', uidb64=uid)
                
            except Exception as e:
                logger.error(f"Signup error: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
    else:
        form = SignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def verify_email_pending(request, uidb64):
    """
    Page shown after signup, reminding user to check email.
    """
    return render(request, 'accounts/verify_email_pending.html', {'uidb64': uidb64})


def verify_email(request, uidb64, token):
    """
    Email verification view.
    
    User receives link with uid and token in email.
    Process:
    1. Decode user ID from uidb64
    2. Verify token is valid and not expired
    3. Activate user account
    4. Mark email as verified
    5. Redirect to login
    """
    try:
        uid = decode_uid(uidb64)
        user = User.objects.get(pk=uid)
        user_profile = user.profile
        
        # Verify token is valid and not expired (24 hours)
        if not email_verification_token.check_token(user, token):
            messages.error(request, 'Verification link is invalid or has expired.')
            return redirect('accounts:signup')
        
        # Check if already verified
        if user_profile.email_verified:
            messages.info(request, 'Your email is already verified. Please login.')
            return redirect('accounts:login')
        
        # Activate user and mark email as verified
        user.is_active = True
        user.save()
        
        user_profile.email_verified = True
        user_profile.email_verification_token = None
        user_profile.email_verification_created = None
        user_profile.save()
        
        logger.info(f"User {user.email} verified email successfully")
        messages.success(request, 'Email verified successfully! You can now login.')
        return redirect('accounts:login')
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('accounts:signup')
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        messages.error(request, 'An error occurred during email verification.')
        return redirect('accounts:signup')


def verify_email_reminder(request):
    """Page to remind user to verify email."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'accounts/verify_email_reminder.html')


def login_view(request):
    """
    User login view.
    
    Security features:
    - Email verification required
    - Session timeout: 15 minutes of inactivity
    - CSRF protection enabled
    - Failed login attempt logging
    
    Process:
    1. User submits email and password
    2. Verify user exists and is active
    3. Verify email is verified
    4. Authenticate credentials
    5. Create session with 15-minute timeout
    6. Redirect to dashboard
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                # Get user by email
                user = User.objects.get(email=email)
                
                # Check if user is active
                if not user.is_active:
                    messages.error(
                        request,
                        'Account is not active. Please verify your email first.'
                    )
                    return redirect('accounts:signup')
                
                # Check if email is verified
                if not user.profile.email_verified:
                    messages.error(
                        request,
                        'Please verify your email before logging in.'
                    )
                    return redirect('accounts:verify_email_reminder')
                
                # Authenticate user
                user = authenticate(request, username=email, password=password)
                
                if user is not None:
                    # Login successful - session created with 15-min timeout
                    login(request, user)
                    logger.info(f"User {email} logged in successfully")
                    messages.success(request, f'Welcome back, {user.email}!')
                    return redirect('accounts:dashboard')
                else:
                    messages.error(request, 'Invalid email or password.')
                    logger.warning(f"Failed login attempt for {email}")
                    
            except User.DoesNotExist:
                # Don't reveal if email exists (security best practice)
                messages.error(request, 'Invalid email or password.')
                logger.warning(f"Login attempt with non-existent email: {email}")
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                messages.error(request, 'An error occurred during login.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url='accounts:login')
def logout_view(request):
    """
    User logout view.
    
    Security:
    - Destroys session completely
    - Clears all session data
    - User must re-authenticate to access protected pages
    """
    email = request.user.email
    logout(request)
    logger.info(f"User {email} logged out")
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


# ============================================================================
# PASSWORD RESET VIEWS
# ============================================================================

def password_reset_request(request):
    """
    Password reset request view.
    
    Flow:
    1. User enters email
    2. Check if email exists
    3. Generate secure reset token
    4. Send reset link via email
    5. Confirm message shown (doesn't reveal if email exists for security)
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                user = User.objects.get(email=email)
                
                # Generate reset token
                uid = encode_uid(user.pk)
                token = password_reset_token.make_token(user)
                
                # Save token to user profile
                user_profile = user.profile
                user_profile.password_reset_token = token
                user_profile.password_reset_created = now()
                user_profile.save()
                
                # Send reset email
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                email_subject = 'Password Reset - Authentication System'
                email_body = f"""
Hello {email},

We received a request to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 24 hours.

If you did not request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
Authentication System Team
"""
                
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                logger.info(f"Password reset requested for {email}")
                
            except User.DoesNotExist:
                pass  # Security: don't reveal if email exists
            except Exception as e:
                logger.error(f"Password reset request error: {str(e)}")
            
            # Show same message regardless of email existence (security)
            messages.success(
                request,
                'If an account exists with this email, you will receive password reset instructions.'
            )
            return redirect('accounts:login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    """
    Password reset confirmation view.
    
    User clicks email link and arrives here.
    Process:
    1. Verify token and user exist
    2. Display password reset form
    3. Validate new password meets requirements
    4. Update password
    5. Redirect to login
    """
    try:
        uid = decode_uid(uidb64)
        user = User.objects.get(pk=uid)
        user_profile = user.profile
        
        # Verify token is valid and not expired (24 hours)
        if not password_reset_token.check_token(user, token):
            messages.error(request, 'Password reset link is invalid or has expired.')
            return redirect('accounts:password_reset_request')
        
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                
                # Update password
                user.set_password(password)
                user.save()
                
                # Clear reset token
                user_profile.password_reset_token = None
                user_profile.password_reset_created = None
                user_profile.save()
                
                logger.info(f"Password reset successful for {user.email}")
                messages.success(request, 'Password has been reset successfully. Please login with your new password.')
                return redirect('accounts:login')
        else:
            form = PasswordResetForm()
        
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:password_reset_request')
    except Exception as e:
        logger.error(f"Password reset confirm error: {str(e)}")
        messages.error(request, 'An error occurred during password reset.')
        return redirect('accounts:password_reset_request')


# ============================================================================
# DASHBOARD VIEWS
# ============================================================================

@login_required(login_url='accounts:login')
def dashboard(request):
    """
    User dashboard - accessible only to authenticated users with verified email.
    
    Shows user information and links based on role.
    """
    try:
        if not request.user.profile.is_email_verified():
            messages.warning(request, 'Please verify your email first.')
            return redirect('accounts:verify_email_reminder')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('accounts:logout')
    
    return render(request, 'accounts/dashboard.html')


@login_required(login_url='accounts:login')
def admin_dashboard(request):
    """
    Admin dashboard - accessible only to admin users.
    
    Shows admin-specific information like user statistics.
    """
    try:
        if not request.user.profile.is_admin():
            messages.error(request, 'You do not have admin access.')
            return redirect('accounts:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('accounts:logout')
    
    total_users = User.objects.count()
    verified_users = UserProfile.objects.filter(email_verified=True).count()
    admin_users = UserProfile.objects.filter(role='admin').count()
    
    context = {
        'total_users': total_users,
        'verified_users': verified_users,
        'admin_users': admin_users,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


# ============================================================================
# HOME PAGE
# ============================================================================

def index(request):
    """Home page - redirects to dashboard if logged in."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/index.html')

