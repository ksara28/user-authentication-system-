import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

EMAIL = 'sara1228k@gmail.com'
PASSWORD = 'SaraTest123!'

try:
    user, created = User.objects.get_or_create(email=EMAIL, defaults={
        'username': EMAIL,
        'is_active': True,
    })
    if created:
        user.set_password(PASSWORD)
        user.save()
        print(f"Created new user: {EMAIL}")
    else:
        print(f"User exists, updating password & activation: {EMAIL}")
        user.set_password(PASSWORD)
        user.is_active = True
        user.save()

    profile, p_created = UserProfile.objects.get_or_create(user=user)
    profile.email_verified = True
    if not profile.role:
        profile.role = 'user'
    profile.save()

    print('Profile verified. Login credentials:')
    print('Email:', EMAIL)
    print('Password:', PASSWORD)
    print('Login URL: http://127.0.0.1:8000/login')

except Exception as e:
    print('Error:', e)
