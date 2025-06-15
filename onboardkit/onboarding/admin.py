from django.contrib import admin
from .models import OnboardingTemplate, TemplateSection, TemplateItem, UserTask

class TemplateItemInline(admin.TabularInline):
    model = TemplateItem
    extra = 1

class TemplateSectionInline(admin.TabularInline):
    model = TemplateSection
    inlines = [TemplateItemInline]
    extra = 1

@admin.register(OnboardingTemplate)
class TemplateAdmin(admin.ModelAdmin):
    inlines = [TemplateSectionInline]
    list_display = ('name', 'role', 'created_by')

@admin.register(UserTask)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_task_title', 'status', 'due_date')
    list_filter = ('status', 'assigned_by')
    search_fields = ('user__username',)
    
    def get_task_title(self, obj):
        return obj.get_task_title()
    get_task_title.short_description = 'Task'