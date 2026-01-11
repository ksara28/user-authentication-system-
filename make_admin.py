#!/usr/bin/env python
"""Make a user an admin"""
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
    user.profile.role = 'admin'
    user.profile.save()
    
    print(f"✅ {email} is now an ADMIN")
    print(f"   Admin dashboard: http://localhost:8000/admin-dashboard/")
    
except User.DoesNotExist:
    print(f"❌ User not found: {email}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
