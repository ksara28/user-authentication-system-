import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

# Create test user
try:
    user = User.objects.create_user(
        username='testuser@example.com',
        email='testuser@example.com',
        password='TestPass123!',
        is_active=True
    )
    
    profile = UserProfile.objects.create(
        user=user,
        role='user',
        email_verified=True
    )
    
    print(f"✅ Successfully created user: {user.email}")
    print(f"Password: TestPass123!")
    print(f"\nYou can now login at: http://127.0.0.1:8000/login/")
    
except Exception as e:
    print(f"❌ Error: {e}")
