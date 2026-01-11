"""
Script to create a user and generate a password reset link
This demonstrates the full password reset flow
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from accounts.tokens import password_reset_token, encode_uid
from django.utils.timezone import now

EMAIL = 'sara1228k@gmail.com'
PASSWORD = 'TestPassword123!'

print("=" * 70)
print("STEP 1: Creating User Account (Simulating Signup)")
print("=" * 70)

# Create or get user
user, created = User.objects.get_or_create(email=EMAIL, defaults={
    'username': EMAIL,
    'is_active': False,  # Inactive until email verified (as per signup flow)
})

if created:
    user.set_password(PASSWORD)
    user.save()
    print(f"✓ Created new user: {EMAIL}")
else:
    print(f"✓ User already exists: {EMAIL}")
    user.set_password(PASSWORD)
    user.save()
    print(f"✓ Updated password to: {PASSWORD}")

# Create or update profile
profile, p_created = UserProfile.objects.get_or_create(user=user)
print(f"✓ Profile exists with role: {profile.role}")

print("\n" + "=" * 70)
print("STEP 2: Email Verification (Required before login)")
print("=" * 70)
print("In normal flow, user would receive verification email.")
print("Manually verifying for testing purposes...")

# Verify email (skip email sending for this demo)
user.is_active = True
user.save()
profile.email_verified = True
profile.save()

print(f"✓ Email verified")
print(f"✓ User can now login with:")
print(f"  Email: {EMAIL}")
print(f"  Password: {PASSWORD}")
print(f"  URL: http://127.0.0.1:8000/login")

print("\n" + "=" * 70)
print("STEP 3: Generate Password Reset Link")
print("=" * 70)

# Generate password reset token
uid = encode_uid(user.pk)
token = password_reset_token.make_token(user)

# Save token to profile (as done in views.py)
profile.password_reset_token = token
profile.password_reset_created = now()
profile.save()

# Generate reset URL
reset_url = f"http://127.0.0.1:8000/password-reset/{uid}/{token}/"

print(f"✓ Password reset token generated")
print(f"\nPassword Reset Link (valid for 24 hours):")
print(f"{reset_url}")

print("\n" + "=" * 70)
print("WHAT WOULD BE IN THE EMAIL:")
print("=" * 70)
email_content = f"""
Subject: Password Reset - Authentication System

Hello {EMAIL},

We received a request to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 24 hours.

If you did not request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
Authentication System Team
"""
print(email_content)

print("=" * 70)
print("TESTING INSTRUCTIONS:")
print("=" * 70)
print("1. Make sure Django server is running:")
print("   python manage.py runserver")
print()
print("2. Visit the password reset link above in your browser")
print()
print("3. Enter a new password (must meet requirements):")
print("   - Minimum 8 characters")
print("   - At least 1 uppercase letter")
print("   - At least 1 lowercase letter")
print("   - At least 1 digit")
print("   - At least 1 special character")
print()
print("4. After resetting, login at:")
print("   http://127.0.0.1:8000/login")
print("=" * 70)
