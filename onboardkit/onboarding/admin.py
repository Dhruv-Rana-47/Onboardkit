from django.contrib import admin
from .models import (
    OnboardingTemplate, TemplateSection, TemplateItem,
    UserTask, TaskFeedback, TemplateAssignment
)


class TemplateItemInline(admin.TabularInline):
    model = TemplateItem
    extra = 1


class TemplateSectionInline(admin.TabularInline):
    model = TemplateSection
    extra = 1


@admin.register(OnboardingTemplate)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'created_by', 'created_at')
    inlines = [TemplateSectionInline]


@admin.register(TemplateSection)
class TemplateSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'template', 'order')
    ordering = ('template', 'order')


@admin.register(TemplateItem)
class TemplateItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'item_type', 'order')
    ordering = ('section', 'order')


@admin.register(UserTask)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_task_title', 'status', 'priority', 'due_date', 'assigned_by')
    list_filter = ('status', 'priority', 'assigned_by')
    search_fields = ('user__username', 'custom_task')

    def get_task_title(self, obj):
        return obj.get_task_title()
    get_task_title.short_description = 'Task'


@admin.register(TaskFeedback)
class TaskFeedbackAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    search_fields = ('task__user__username', 'comment')


@admin.register(TemplateAssignment)
class TemplateAssignmentAdmin(admin.ModelAdmin):
    list_display = ('template', 'assignee', 'assigned_by', 'due_date', 'is_completed')
    list_filter = ('is_completed', 'assigned_date', 'due_date')
    search_fields = ('template__name', 'assignee__username', 'assigned_by__username')
