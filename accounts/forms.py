"""
Authentication forms with custom validation.
Handles signup, login, and password reset with:
- Email format validation
- Password strength validation
- Duplicate email prevention
- CSRF protection (automatic with Django forms)
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class SignupForm(forms.Form):
    """
    User registration form with comprehensive validation.
    
    Validates:
    - Email format and uniqueness
    - Password strength (minimum 8 chars, uppercase, lowercase, number, special char)
    - Password confirmation match
    """
    
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True
        })
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password (min 8 chars)',
            'required': True
        })
    )
    password_confirm = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        })
    )
    
    def clean_email(self):
        """Validate email is unique and properly formatted."""
        email = self.cleaned_data.get('email', '').lower()
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                'An account with this email already exists. Please login instead.',
                code='email_exists'
            )
        
        return email
    
    def clean_password(self):
        """
        Validate password strength.
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        password = self.cleaned_data.get('password', '')
        
        if len(password) < 8:
            raise ValidationError(
                'Password must be at least 8 characters long.',
                code='password_too_short'
            )
        
        # Check for uppercase
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                'Password must contain at least one uppercase letter.',
                code='password_no_upper'
            )
        
        # Check for lowercase
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                'Password must contain at least one lowercase letter.',
                code='password_no_lower'
            )
        
        # Check for digit
        if not re.search(r'\d', password):
            raise ValidationError(
                'Password must contain at least one digit.',
                code='password_no_digit'
            )
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                'Password must contain at least one special character (!@#$%^&*etc).',
                code='password_no_special'
            )
        
        return password
    
    def clean(self):
        """Validate password and confirmation match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError(
                    'Passwords do not match.',
                    code='password_mismatch'
                )
        
        return cleaned_data


class LoginForm(forms.Form):
    """
    Login form with email and password validation.
    
    Note: Actual credential verification happens in the view,
    not in the form (Django best practice).
    """
    
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': True
        })
    )
    
    def clean_email(self):
        """Convert email to lowercase for consistency."""
        email = self.cleaned_data.get('email', '').lower()
        return email


class PasswordResetRequestForm(forms.Form):
    """
    Form to request password reset.
    User enters email and receives reset link via email.
    """
    
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True
        })
    )
    
    def clean_email(self):
        """Check if email exists in system."""
        email = self.cleaned_data.get('email', '').lower()
        
        if not User.objects.filter(email=email).exists():
            raise ValidationError(
                'No account found with this email address.',
                code='email_not_found'
            )
        
        return email


class PasswordResetForm(forms.Form):
    """
    Form for setting new password during password reset.
    Uses same validation as SignupForm for password strength.
    """
    
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (min 8 chars)',
            'required': True
        })
    )
    password_confirm = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'required': True
        })
    )
    
    def clean_password(self):
        """Validate password strength (same as SignupForm)."""
        password = self.cleaned_data.get('password', '')
        
        if len(password) < 8:
            raise ValidationError(
                'Password must be at least 8 characters long.',
                code='password_too_short'
            )
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                'Password must contain at least one uppercase letter.',
                code='password_no_upper'
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                'Password must contain at least one lowercase letter.',
                code='password_no_lower'
            )
        
        if not re.search(r'\d', password):
            raise ValidationError(
                'Password must contain at least one digit.',
                code='password_no_digit'
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                'Password must contain at least one special character.',
                code='password_no_special'
            )
        
        return password
    
    def clean(self):
        """Validate password and confirmation match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError(
                    'Passwords do not match.',
                    code='password_mismatch'
                )
        
        return cleaned_data
