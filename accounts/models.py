from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Choice constants for user roles
ROLE_CHOICES = (
    ('user', 'User'),
    ('admin', 'Admin'),
)


class UserProfile(models.Model):
    """
    Extended User Profile for Role-Based Access Control (RBAC)
    and Email Verification tracking.
    
    One-to-One relationship with Django's built-in User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    email_verified = models.BooleanField(default=False)  # Email verification tracking
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_created = models.DateTimeField(blank=True, null=True)
    
    # Password reset token
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_created = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'
    
    def is_email_verified(self):
        """Check if email is verified."""
        return self.email_verified

