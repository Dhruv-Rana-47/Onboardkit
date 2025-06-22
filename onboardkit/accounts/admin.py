from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role

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
    
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_to', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('report_to',)
    ordering = ('name',)
    fields = ('name', 'report_to', 'authorities', 'description')