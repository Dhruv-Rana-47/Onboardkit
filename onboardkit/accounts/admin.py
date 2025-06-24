from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Company, Profile


# Customize how users appear in admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'mentor', 'company')}),
    )
admin.site.register(User, CustomUserAdmin)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_department')

    def get_department(self, obj):
        return obj.user.department.name if obj.user.department else "-"
    get_department.short_description = 'Department'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'report_to', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('company', 'report_to')
    ordering = ('name',)
    fields = ('name', 'company', 'report_to', 'authorities', 'description')
