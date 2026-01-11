# Django Environment Setup Guide

This document provides step-by-step instructions to set up real Google OAuth and Gmail SMTP authentication.

## Prerequisites
- A Google Account
- Python 3.8+
- Django 6.0.1
- django-allauth installed

---

## Part 1: Google Cloud Console Setup (OAuth)

### 1.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "NEW PROJECT"
4. Name it "Auth System" (or any name you prefer)
5. Click "CREATE"

### 1.2 Configure OAuth Consent Screen
1. In the left sidebar, go to **APIs & Services** > **OAuth consent screen**
2. Select **External** (for testing/personal use)
3. Click **CREATE**
4. Fill in the form:
   - **App name**: Django Auth System
   - **User support email**: your-email@gmail.com
   - **Developer contact**: your-email@gmail.com
5. Click **SAVE AND CONTINUE**
6. On "Scopes" page, click **SAVE AND CONTINUE** (default scopes are fine)
7. On "Test users" page, add your email and click **SAVE AND CONTINUE**

### 1.3 Create OAuth Client ID
1. Go to **APIs & Services** > **Credentials**
2. Click **CREATE CREDENTIALS** > **OAuth client ID**
3. Select **Web application**
4. Name it "Django Auth"
5. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:8000
   http://127.0.0.1:8000
   ```
6. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
7. Click **CREATE**
8. A popup will show your **Client ID** and **Client Secret** — copy both

---

## Part 2: Gmail App Password Setup

### 2.1 Enable 2-Step Verification
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. In the left sidebar, click **Security**
3. Scroll to **2-Step Verification**
4. If not enabled, click to enable it and follow the prompts

### 2.2 Create App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under **App passwords** (you'll see this only if 2-Step Verification is enabled)
3. Select:
   - **App**: Mail
   - **Device**: Windows (or Mac/Linux)
4. Click **GENERATE**
5. Google will show a 16-character password like: `abcd efgh ijkl mnop`
6. Copy this password (including spaces)

---

## Part 3: Environment Setup (.env)

### 3.1 Create `.env` File
1. In your project root, create a file named `.env`
2. Copy the contents of `.env.example`:
   ```bash
   cp .env.example .env
   ```

### 3.2 Update `.env` with Your Credentials

**Edit the `.env` file and replace:**

```dotenv
# Gmail SMTP
EMAIL_HOST_USER=your.real.email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop

# Google OAuth (from step 1.3)
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_key_here
```

> **Important**: Keep `.env` private! Never commit it to Git. It's already in `.gitignore`.

---

## Part 4: Django Setup

### 4.1 Run Setup Command
```bash
python manage.py setup_social_auth
```

This command will:
- Create the Site object (required for Allauth)
- Create the Google SocialApp and link it to the Site
- Load credentials from your `.env` file

**Expected output:**
```
✓ Created Site: Django Auth System (localhost:8000)
✓ Created Google SocialApp
  Client ID: 1234567890-abcde...
  Secret: GOCSPX-your_secret...
✓ Linked Google OAuth to Site

✅ Setup complete! You can now:
  1. Run: python manage.py runserver
  2. Visit: http://localhost:8000/login/
  3. Click "Login with Google" to test OAuth flow
```

### 4.2 Run the Server
```bash
python manage.py runserver
```

### 4.3 Test Google Login
1. Open http://localhost:8000/login/
2. Click **"Login with Google"**
3. You'll be redirected to Google's login page
4. Sign in with your Google account
5. Grant permissions
6. You'll be redirected back and logged into the system
7. A `UserProfile` will be automatically created

### 4.4 Test Password Reset (Gmail SMTP)
1. Go to http://localhost:8000/login/
2. Click **"Forgot your password?"**
3. Enter your email
4. Check your inbox for the password reset email (sent via Gmail)
5. Click the link to reset your password

---

## Troubleshooting

### "Google client not found" or "SocialApp matching query does not exist"
**Solution**: Run `python manage.py setup_social_auth` to create the SocialApp.

### "Invalid client" error during Google login
**Solution**: 
- Double-check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
- Ensure redirect URIs in Google Console match exactly

### Password reset email not sending
**Solution**:
- Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `.env`
- Ensure you're using the **App Password**, not your regular Gmail password
- Check that 2-Step Verification is enabled on your Google Account

### "CSRF verification failed"
**Solution**: Ensure `CSRF_TRUSTED_ORIGINS` in `.env` includes your host and port.

---

## Security Notes

✅ **Before Production:**
1. Change `DEBUG=False`
2. Set a strong `SECRET_KEY`
3. Use environment variables (never hardcode secrets)
4. Set `EMAIL_USE_TLS=True` and verify SSL certificates
5. Use HTTPS only (set `CSRF_COOKIE_SECURE=True`)
6. Store `.env` securely (never commit to Git)

---

## Files Reference

- `.env.example` — Template with placeholder credentials
- `.env` — Your actual credentials (git-ignored, **keep it private**)
- `accounts/management/commands/setup_social_auth.py` — Management command to auto-setup Site and SocialApp
