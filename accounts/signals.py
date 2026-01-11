from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created.
    This ensures Google OAuth and manual signup users both have profiles.
    """
    if created:
        # Check if profile already exists (to avoid conflicts with manual signup)
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(
                user=instance,
                role='user',
                email_verified=True  # Google users are verified by default
            )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile whenever the User is saved.
    Ensures profile stays in sync with user updates.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
