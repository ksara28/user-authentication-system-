#!/usr/bin/env python
"""Manually verify user email"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

email = 'sara1228k@gmail.com'

try:
    user = User.objects.get(email=email)
    print(f"User found: {user.email}")
    print(f"Is active: {user.is_active}")
    
    # Activate user
    user.is_active = True
    user.save()
    
    # Mark email as verified
    user.profile.email_verified = True
    user.profile.save()
    
    print(f"\n✅ Account activated!")
    print(f"✅ Email marked as verified!")
    print(f"\nYou can now login at: http://localhost:8000/login/")
    
except User.DoesNotExist:
    print(f"❌ User not found: {email}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
