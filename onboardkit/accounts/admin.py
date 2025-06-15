from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Customize how users appear in admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'mentor')}),
    )

admin.site.register(User, CustomUserAdmin)

# accounts/admin.py
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    search_fields = ('user__username', 'bio')