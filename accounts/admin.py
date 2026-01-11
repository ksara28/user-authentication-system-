from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline display of UserProfile in User admin."""
    model = UserProfile
    fields = ('role', 'email_verified', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class UserAdmin(admin.ModelAdmin):
    """Custom User admin with UserProfile inline."""
    list_display = ('email', 'username', 'is_active', 'date_joined')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')
    inlines = [UserProfileInline]


class UserProfileAdmin(admin.ModelAdmin):
    """UserProfile admin interface."""
    list_display = ('user', 'role', 'email_verified', 'created_at')
    list_filter = ('role', 'email_verified', 'created_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('email_verification_created', 'password_reset_created', 'created_at', 'updated_at')
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Role & Permissions', {
            'fields': ('role',)
        }),
        ('Email Verification', {
            'fields': ('email_verified', 'email_verification_token', 'email_verification_created')
        }),
        ('Password Reset', {
            'fields': ('password_reset_token', 'password_reset_created')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Register models
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

