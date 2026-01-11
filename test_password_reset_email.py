#!/usr/bin/env python
"""Test password reset email sending"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from accounts.tokens import password_reset_token, encode_uid
from django.utils.timezone import now
from accounts.models import UserProfile

email = 'sara1228k@gmail.com'

try:
    user = User.objects.get(email=email)
    print(f"✅ Found user: {user.email}")
    
    # Generate reset token (same as view does)
    uid = encode_uid(user.pk)
    token = password_reset_token.make_token(user)
    
    # Save token to profile
    user_profile = user.profile
    user_profile.password_reset_token = token
    user_profile.password_reset_created = now()
    user_profile.save()
    print(f"✅ Token saved to profile")
    
    # Construct reset URL
    reset_url = f"http://localhost:8000/password-reset/{uid}/{token}/"
    
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
    
    print(f"\nSending email to: {email}")
    print(f"From: {settings.DEFAULT_FROM_EMAIL}")
    
    send_mail(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    
    print(f"✅ Password reset email sent successfully!")
    print(f"\nReset link: {reset_url}")
    
except User.DoesNotExist:
    print(f"❌ User not found: {email}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
