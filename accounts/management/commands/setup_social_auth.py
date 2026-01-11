import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Setup Site and Google SocialApp from environment variables'

    def handle(self, *args, **options):
        """
        Automatically create or update the Site and Google OAuth SocialApp.
        Reads from environment variables: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
        """
        
        # Get Google credentials from environment
        google_client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
        
        if not google_client_id or not google_client_secret:
            raise CommandError(
                'ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables must be set.\n'
                'Get these from Google Cloud Console > Credentials > OAuth Client ID.\n'
                'Update your .env file and try again.'
            )
        
        # Setup Site (required for Allauth)
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'Django Auth System'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created Site: {site.name} ({site.domain})')
            )
        else:
            self.stdout.write(f'ℹ Site already exists: {site.name} ({site.domain})')
        
        # Setup Google SocialApp
        try:
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google OAuth',
                    'client_id': google_client_id,
                    'secret': google_client_secret,
                }
            )
            
            # Update if credentials changed
            if not created and (google_app.client_id != google_client_id or google_app.secret != google_client_secret):
                google_app.client_id = google_client_id
                google_app.secret = google_client_secret
                google_app.save()
                self.stdout.write(self.style.SUCCESS('✓ Updated Google OAuth credentials'))
            
            # Ensure the app is linked to the site
            if not google_app.sites.filter(pk=1).exists():
                google_app.sites.add(site)
                self.stdout.write(self.style.SUCCESS('✓ Linked Google OAuth to Site'))
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created Google SocialApp\n'
                    f'  Client ID: {google_client_id[:20]}...\n'
                    f'  Secret: {google_client_secret[:10]}...')
                )
            else:
                self.stdout.write(f'✓ Google OAuth app is ready')
        
        except IntegrityError as e:
            raise CommandError(f'Error setting up Google SocialApp: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Setup complete! You can now:\n'
                '  1. Run: python manage.py runserver\n'
                '  2. Visit: http://localhost:8000/login/\n'
                '  3. Click "Login with Google" to test OAuth flow'
            )
        )
