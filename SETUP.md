# Quick Start Guide

## 5-Minute Setup

### Step 1: Activate Virtual Environment

```bash
cd "user authentication system"

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Step 2: Install Dependencies (if not already installed)

```bash
pip install -r requirements.txt
```

### Step 3: Run Migrations

```bash
python manage.py migrate
```

### Step 4: Create Admin User

```bash
python manage.py createsuperuser
```

Example:
- Email: `admin@example.com`
- Password: `AdminPass123!`

### Step 5: Start Server

```bash
python manage.py runserver
```

Server will start at `http://localhost:8000`

---

## Testing the System

### 1. **Home Page**
- URL: `http://localhost:8000/`
- Shows features and links to signup/login

### 2. **Signup**
- URL: `http://localhost:8000/signup/`
- Test password: `TestPass123!`
- Email format: `test@example.com`
- You'll see "Check your email" message

### 3. **Email Verification (Development)**
- In development, emails won't actually send
- To test verification, use Django shell:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import UserProfile

# Get the user you just created
user = User.objects.get(email='test@example.com')

# Manually verify for testing
user_profile = user.profile
user_profile.email_verified = True
user_profile.save()

# Activate user
user.is_active = True
user.save()

exit()
```

### 4. **Login**
- URL: `http://localhost:8000/login/`
- Email: `test@example.com`
- Password: (same as signup)
- Should see dashboard after login

### 5. **Dashboard**
- URL: `http://localhost:8000/dashboard/`
- Shows user info and session timeout info
- Only accessible if logged in and email verified

### 6. **Admin Dashboard**
- URL: `http://localhost:8000/admin-dashboard/`
- Shows system statistics
- **Only accessible with admin role**
- Create admin user in Django shell:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import UserProfile

# Get a user
user = User.objects.get(email='test@example.com')

# Update profile to admin
user_profile = user.profile
user_profile.role = 'admin'
user_profile.save()

exit()
```

### 7. **Django Admin Panel**
- URL: `http://localhost:8000/admin/`
- Login with superuser credentials
- Manage users, profiles, and permissions

---

## Email Configuration (Production)

### Gmail Setup

1. **Enable 2-Factor Authentication**: https://myaccount.google.com/security
2. **Generate App Password**: https://myaccount.google.com/apppasswords
3. **Copy App Password** and add to `.env`:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

### Other Email Providers

**SendGrid:**
```bash
pip install sendgrid-django
```

**AWS SES:**
```bash
pip install django-ses
```

See README.md for detailed setup.

---

## Session Timeout Testing

1. Login to dashboard
2. Wait 15 minutes without making any requests
3. Try to access dashboard again
4. Should be redirected to login page

### Change Timeout Duration

Edit `auth_system/settings.py`:

```python
SESSION_COOKIE_AGE = 900  # Change to desired seconds
# 900 = 15 minutes
# 1800 = 30 minutes
# 3600 = 1 hour
```

---

## Password Requirements

User passwords must have:
- ✅ Minimum 8 characters
- ✅ At least one UPPERCASE letter (A-Z)
- ✅ At least one lowercase letter (a-z)
- ✅ At least one digit (0-9)
- ✅ At least one special character (!@#$%^&*)

Example valid password: `MyPass123!`

---

## Database Reset

To delete all data and start fresh:

```bash
# Delete database file
del db.sqlite3

# Run migrations again
python manage.py migrate

# Create new admin user
python manage.py createsuperuser
```

---

## File Structure Quick Reference

```
accounts/                      # Authentication app
├── forms.py                  # Form validation
├── models.py                 # UserProfile model
├── views.py                  # All authentication logic
├── tokens.py                 # Email/password tokens
├── urls.py                   # URL routing
├── admin.py                  # Django admin
└── templates/accounts/       # HTML templates
    ├── base.html            # Base template
    ├── signup.html
    ├── login.html
    ├── dashboard.html
    └── ...

auth_system/                   # Main project
├── settings.py              # Configuration
├── urls.py                  # Main URL router
└── wsgi.py                  # Production server

manage.py                      # Django CLI
.env                          # Environment variables
requirements.txt             # Python dependencies
README.md                     # Full documentation
```

---

## Common Issues & Solutions

### Email sending doesn't work?
- Check `.env` file has correct EMAIL settings
- Gmail: Use App Password, not regular password
- Check console for error messages
- In development, emails won't send if EMAIL_HOST_PASSWORD is wrong

### Migration errors?
```bash
python manage.py migrate --fake accounts
python manage.py makemigrations accounts
python manage.py migrate
```

### Permission denied error on dashboard?
- Check if email is verified
- Check if user role is correct
- For admin features, role must be 'admin'

### Session not timing out?
- Clear browser cookies
- Verify `SESSION_SAVE_EVERY_REQUEST = True` in settings.py
- Check that 15 minutes have actually passed

### "Page not found" 404 error?
- Check URL is correct
- Make sure you're logged in if page requires authentication
- Make sure email is verified if page requires verification

---

## Security Checklist

Before production deployment:

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Set up HTTPS/SSL certificate
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure proper email backend
- [ ] Set up monitoring and logging
- [ ] Regular backups of database

---

## Useful Django Commands

```bash
# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Create test data
python manage.py shell < seed_data.py

# Show all URLs
python manage.py show_urls

# Check for issues
python manage.py check

# Collect static files (production)
python manage.py collectstatic
```

---

## Support

Refer to **README.md** for:
- Complete feature list
- Authentication flow diagrams
- Database schema
- Production deployment guide
- API endpoint planning
- Troubleshooting section

---

**Last Updated**: January 2026
**Django Version**: 6.0+
**Status**: Production-Ready ✅
