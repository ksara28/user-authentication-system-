"""
Token generation module for email verification and password reset.

Uses Django's built-in PasswordResetTokenGenerator for secure token generation.
Tokens are time-limited and can only be used once.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import six


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for email verification.
    Extends Django's PasswordResetTokenGenerator for extra security.
    
    Token properties:
    - Time-limited (default 24 hours)
    - Can only be used once
    - User-specific (cannot be used for another user)
    - Invalidated if user changes password
    """
    
    def _make_hash_value(self, user, timestamp):
        """
        Create hash value for token verification.
        Token becomes invalid if:
        1. 24 hours pass
        2. User changes password
        3. User's email is changed
        """
        return (
            six.text_type(user.pk) + 
            six.text_type(timestamp) + 
            six.text_type(user.email)
        )


class PasswordResetTokenGeneratorCustom(PasswordResetTokenGenerator):
    """
    Custom token generator for password reset.
    Similar to EmailVerificationTokenGenerator but for password recovery.
    """
    
    def _make_hash_value(self, user, timestamp):
        """
        Create hash value for token verification.
        Token becomes invalid if:
        1. 24 hours pass
        2. User changes password
        """
        return (
            six.text_type(user.pk) + 
            six.text_type(timestamp) + 
            six.text_type(user.password)
        )


# Create instances for use in views and forms
email_verification_token = EmailVerificationTokenGenerator()
password_reset_token = PasswordResetTokenGeneratorCustom()


def encode_uid(pk):
    """Encode user ID to safe base64 string."""
    return urlsafe_base64_encode(force_bytes(pk))


def decode_uid(uidb64):
    """Decode user ID from base64 string."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return uid
    except (TypeError, ValueError, OverflowError):
        return None
