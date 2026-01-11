# Production-Ready Django Authentication System

A complete, production-grade user authentication system built with Django featuring email verification, password reset, role-based access control (RBAC), and automatic session timeout.

## 📋 Features

### ✅ Core Authentication
- **User Signup**: Email + strong password registration
- **Email Verification**: Token-based email verification (24-hour expiry)
- **User Login**: Email + password with verified email requirement
- **User Logout**: Secure session termination
- **Password Reset**: Token-based password recovery

### 🔐 Security Features
- **Password Hashing**: Django's PBKDF2 algorithm
- **Password Strength**: Minimum 8 characters, uppercase, lowercase, digit, special character
- **CSRF Protection**: Built-in on all forms
- **Session Timeout**: Automatic logout after 15 minutes of inactivity
- **Email Verification**: Prevents unauthorized email access
- **Token Expiry**: 24-hour expiry for verification and reset tokens
- **Secure Tokens**: Time-limited, user-specific, invalidated on password change

### 👥 Role-Based Access Control (RBAC)
- **Two Roles**: Admin and User
- **Admin Dashboard**: System statistics and user management
- **User Dashboard**: Personal account information
- **Route Protection**: Decorators enforce role-based access

### 🛠️ Technical Stack
- **Backend**: Django 6.0+
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **Email**: SMTP (Gmail tested)
- **Frontend**: HTML + CSS (responsive)
- **Session Storage**: Database-backed sessions
- **Configuration**: Environment variables (.env)

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual environment

### 1. Clone or Download Project

```bash
cd "user authentication system"
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Django
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Generate at https://myaccount.google.com/apppasswords
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 7. Create Test Admin User

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import UserProfile

# Create test user
user = User.objects.create_user(
    username='testadmin@example.com',
    email='testadmin@example.com',
    password='TestPassword123!',
    is_active=True
)

# Create admin profile with verified email
profile = UserProfile.objects.create(
    user=user,
    role='admin',
    email_verified=True
)

exit()
```

### 8. Start Development Server

```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

---

## 📖 Authentication Flow

### 1. **Signup Process**
```
User enters email + password
    ↓
Form validates:
  - Email format & uniqueness
  - Password strength (8+ chars, uppercase, lowercase, digit, special)
    ↓
User created (inactive: is_active=False)
    ↓
UserProfile created with verification token
    ↓
Verification email sent with 24-hour token link
    ↓
User directed to "Check Email" page
```

### 2. **Email Verification**
```
User clicks link in email
    ↓
Token validated (not expired, not used, matches user)
    ↓
User activated (is_active=True)
    ↓
Email marked verified (profile.email_verified=True)
    ↓
User redirected to login
```

### 3. **Login Process**
```
User enters email + password
    ↓
Check if user exists
    ↓
Check if user is active
    ↓
Check if email is verified
    ↓
Authenticate credentials
    ↓
Session created (15-minute timeout on inactivity)
    ↓
User redirected to dashboard
```

### 4. **Session Timeout (15 Minutes)**
```
User logs in
    ↓
Session expires in 15 minutes of INACTIVITY
    ↓
Browser tab stays open but session is dead
    ↓
Next request redirects to login
    ↓
User must re-authenticate
```

**Configuration in `settings.py`:**
```python
SESSION_COOKIE_AGE = 900  # 15 minutes in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True  # Update timeout on each request
```

### 5. **Password Reset**
```
User requests password reset
    ↓
Enter email address
    ↓
Check if email exists (security: same message regardless)
    ↓
Generate secure reset token
    ↓
Send reset email with 24-hour token link
    ↓
User clicks link
    ↓
Token validated
    ↓
User enters new password (validated for strength)
    ↓
Password updated, token cleared
    ↓
User redirected to login
```

---

## 🔑 URL Routes

### Authentication
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page |
| `/signup/` | GET, POST | User registration |
| `/verify-email-pending/<uid>/` | GET | Pending verification page |
| `/verify-email/<uid>/<token>/` | GET | Email verification link |
| `/login/` | GET, POST | User login |
| `/logout/` | GET | User logout |

### Password Recovery
| Route | Method | Description |
|-------|--------|-------------|
| `/password-reset/` | GET, POST | Request password reset |
| `/password-reset/<uid>/<token>/` | GET, POST | Reset password |

### Dashboards
| Route | Method | Description | Access |
|-------|--------|-------------|--------|
| `/dashboard/` | GET | User dashboard | Authenticated + Verified Email |
| `/admin-dashboard/` | GET | Admin dashboard | Admin Role |

---

## 🔒 Security Implementation

### 1. **Password Hashing**
- Uses Django's PBKDF2 hasher (industry standard)
- Passwords never stored in plain text
- Uses `user.set_password()` for hashing
- Validates with `authenticate()` function

### 2. **Email Verification Tokens**
- Generated using `EmailVerificationTokenGenerator`
- Time-limited (24 hours)
- User-specific (includes user ID + email)
- Invalidated on password change
- One-time use (token cleared after verification)

### 3. **Password Reset Tokens**
- Similar to email verification tokens
- 24-hour expiry
- User-specific
- Cleared after password reset

### 4. **Session Management**
```
SESSION_COOKIE_AGE = 900  # 15 minutes
SESSION_COOKIE_HTTPONLY = True  # Prevent JS access
SESSION_COOKIE_SECURE = False  # Set True in production
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_SAVE_EVERY_REQUEST = True  # Update on each request
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### 5. **CSRF Protection**
- All POST forms include `{% csrf_token %}`
- Enabled via middleware
- Validates token on form submission

### 6. **Environment Variables**
- Sensitive data in `.env` (not version controlled)
- Loaded with `python-dotenv`
- Includes: SECRET_KEY, EMAIL credentials, database URL

### 7. **Error Handling**
- Generic error messages (don't reveal if email exists)
- Logging of failed login attempts
- Proper exception handling
- No stack traces in production

---

## 📁 Project Structure

```
user-authentication-system/
├── manage.py
├── .env                          # Environment variables
├── .env.example                  # Template for .env
├── requirements.txt              # Python dependencies
├── db.sqlite3                    # Database (created after migrate)
│
├── auth_system/                  # Main project
│   ├── __init__.py
│   ├── settings.py              # Django configuration
│   ├── urls.py                  # Main URL router
│   ├── wsgi.py                  # WSGI configuration
│   └── asgi.py                  # ASGI configuration
│
└── accounts/                     # Authentication app
    ├── migrations/
    │   └── __init__.py
    ├── templates/accounts/       # HTML templates
    │   ├── base.html
    │   ├── index.html
    │   ├── signup.html
    │   ├── login.html
    │   ├── password_reset_request.html
    │   ├── password_reset_confirm.html
    │   ├── dashboard.html
    │   ├── admin_dashboard.html
    │   ├── verify_email_pending.html
    │   └── verify_email_reminder.html
    ├── __init__.py
    ├── admin.py                 # Django admin configuration
    ├── apps.py                  # App configuration
    ├── forms.py                 # Form validation
    ├── models.py                # Database models
    ├── tokens.py                # Token generation
    ├── urls.py                  # App URL routes
    └── views.py                 # View logic
```

---

## 🎨 Customization

### Change Session Timeout
Edit `auth_system/settings.py`:

```python
SESSION_COOKIE_AGE = 1800  # 30 minutes instead of 900 (15 min)
```

### Change Password Requirements
Edit `accounts/forms.py` > `SignupForm.clean_password()`:

```python
# Add your custom validation logic
if len(password) < 12:  # Require 12 characters instead of 8
    raise ValidationError('...')
```

### Change Email Provider
Edit `auth_system/settings.py`:

```python
# For SendGrid
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# For AWS SES
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
```

### Add More User Roles
Edit `accounts/models.py`:

```python
ROLE_CHOICES = (
    ('user', 'User'),
    ('admin', 'Admin'),
    ('moderator', 'Moderator'),  # Add new role
    ('guest', 'Guest'),           # Add new role
)
```

---

## 🧪 Testing

### Test Signup Flow
1. Go to `/signup/`
2. Enter email: `test@example.com`
3. Enter password: `TestPassword123!` (must meet requirements)
4. Click signup
5. Check console for email (development) or email inbox

### Test Email Verification
1. Copy verification link from email
2. Paste in browser
3. Should see "Email verified" message
4. Try to login

### Test Login
1. Go to `/login/`
2. Enter email and password
3. Access dashboard (only if email verified)
4. Session expires after 15 minutes of inactivity

### Test Password Reset
1. Go to `/login/`
2. Click "Forgot your password?"
3. Enter email
4. Check email for reset link
5. Click link and set new password

### Test Session Timeout
1. Login successfully
2. Wait 15 minutes without making any requests
3. Try to access dashboard
4. Should be redirected to login

### Test RBAC
1. Create second user with admin role (in Django shell)
2. Login with admin user
3. Access `/admin-dashboard/`
4. Login with regular user
5. Should get permission denied error

---

## 📊 Database Models

### UserProfile
```python
user              # OneToOne to Django User
role              # 'user' or 'admin'
email_verified    # Boolean (required for login)
email_verification_token
email_verification_created
password_reset_token
password_reset_created
created_at
updated_at
```

---

## 🚢 Production Deployment

### Before Deploying

1. **Update Settings**
```python
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')  # Generate new key
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
```

2. **Use PostgreSQL**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', 5432),
    }
}
```

3. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

4. **Run Migrations**
```bash
python manage.py migrate
```

5. **Use WSGI Server** (Gunicorn, Waitress, etc.)
```bash
gunicorn auth_system.wsgi:application --bind 0.0.0.0:8000
```

6. **Use HTTPS Only**
- Get SSL certificate (Let's Encrypt recommended)
- Configure reverse proxy (Nginx/Apache)
- Set SECURE_SSL_REDIRECT = True

---

## 📝 Logging & Monitoring

View logs in console during development. For production, configure file logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/auth_system.log',
        },
    },
    'loggers': {
        'accounts': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
    },
}
```

---

## 🐛 Troubleshooting

### Emails Not Sending
- Check `.env` EMAIL credentials
- Verify Gmail App Password: https://myaccount.google.com/apppasswords
- Enable "Less secure app access" if needed (not recommended)
- Check server logs for SMTP errors

### Session Not Timing Out
- Verify `SESSION_SAVE_EVERY_REQUEST = True` in settings
- Check `SESSION_COOKIE_AGE = 900`
- Clear browser cookies
- Check database for sessions table

### Email Verification Link Expired
- Default is 24 hours
- Token is invalidated if user changes password
- User can request new signup email

### Permission Denied Errors
- Check user role: Admin vs User
- Verify email is verified
- Check if user is active (is_active=True)

---

## 📚 Django Admin Access

Access Django admin panel at `/admin/`:

```
URL: http://localhost:8000/admin/
Username: (your superuser)
Password: (your superuser password)
```

### Admin Features
- Manage users and profiles
- View email verification status
- Change user roles
- Create test data
- Monitor login attempts

---

## 🔄 API Endpoints (Future Enhancement)

This system is template-based, but can be extended with Django REST Framework:

- `POST /api/auth/signup/` - Register user
- `POST /api/auth/verify-email/` - Verify email
- `POST /api/auth/login/` - Get auth token
- `POST /api/auth/logout/` - Revoke token
- `POST /api/auth/password-reset/` - Request reset
- `POST /api/auth/password-reset-confirm/` - Confirm reset

---

## 📄 License

This project is free to use and modify for educational and commercial purposes.

---

## 👨‍💼 Support

For issues or questions:
1. Check troubleshooting section
2. Review Django documentation: https://docs.djangoproject.com/
3. Check email configuration
4. Run tests and check logs

---

## ✨ Best Practices Implemented

✅ Secure password hashing (PBKDF2)
✅ Email verification required
✅ Token-based password reset
✅ Automatic session timeout (15 minutes)
✅ CSRF protection on all forms
✅ Role-based access control
✅ Environment variable configuration
✅ Comprehensive error handling
✅ Security logging
✅ Production-ready code structure
✅ Responsive HTML/CSS
✅ Clear code comments
✅ Proper separation of concerns
✅ Django best practices

---

**Created**: January 2026
**Django Version**: 6.0+
**Python Version**: 3.8+
