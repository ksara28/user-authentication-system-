#!/usr/bin/env python
"""Quick test script to verify Gmail SMTP credentials"""
import os
from dotenv import load_dotenv
from django.core.mail import send_mail
import django

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')
django.setup()

print("Testing Gmail SMTP connection...")
print(f"Email: {os.getenv('EMAIL_HOST_USER')}")
print(f"Password: {'*' * len(os.getenv('EMAIL_HOST_PASSWORD', ''))}")

try:
    send_mail(
        subject='Test Email from Django',
        message='If you receive this, your Gmail SMTP is working correctly!',
        from_email=os.getenv('EMAIL_HOST_USER'),
        recipient_list=[os.getenv('EMAIL_HOST_USER')],
        fail_silently=False,
    )
    print("\n✅ SUCCESS! Email sent. Check your inbox.")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nCommon fixes:")
    print("1. Generate a NEW App Password at: https://myaccount.google.com/apppasswords")
    print("2. Make sure 2-Step Verification is enabled")
    print("3. Copy the password WITHOUT spaces")
    print("4. Update .env file")
