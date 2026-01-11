#!/usr/bin/env python
"""Check if user exists and test password reset"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

email = 'sara1228k@gmail.com'

# Check if user exists
try:
    user = User.objects.get(email=email)
    print(f"✅ User found: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   First Name: {user.first_name}")
    
    # Check if profile exists
    try:
        profile = user.profile
        print(f"   Profile exists: Yes")
        print(f"   Role: {profile.role}")
        print(f"   Email verified: {profile.email_verified}")
    except UserProfile.DoesNotExist:
        print(f"   ❌ Profile missing! Run: python manage.py migrate")
        
except User.DoesNotExist:
    print(f"❌ No user found with email: {email}")
    print(f"\nAvailable users:")
    for user in User.objects.all():
        print(f"  - {user.username} ({user.email})")
