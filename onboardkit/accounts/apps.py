# accounts/apps.py

from django.apps import AppConfig
import sys

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Avoid running during migrations or when DB isn't ready
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv or 'collectstatic' in sys.argv:
            return

        try:
            from .models import Authority
            from django.db import OperationalError, ProgrammingError

            default_authorities = [
                ("create_user", "Create new user"),
                ("edit_user", "Edit user profile"),
                ("view_users", "View user list"),
                ("assign_user", "Assign user to role"),
                ("view_hierarchy", "View users within hierarchy only"),
                ("view_templates", "View templates"),
                ("create_template", "Create onboarding template"),
                ("edit_template", "Edit template"),
                ("assign_template", "Assign templates to roles/departments"),
                ("create_task", "Create task"),
                ("view_tasks", "View assigned tasks"),
                ("edit_task", "Modify task details"),
                ("complete_task", "Mark task as complete"),
                ("view_progress", "View onboarding progress report"),
                ("view_logs", "View user activity logs"),
                ("view_mentor_info", "View mentor information"),
            ]

            for code, label in default_authorities:
                Authority.objects.get_or_create(code=code, defaults={'label': label})

        except (OperationalError, ProgrammingError):
            # This prevents crashing if DB isn't fully migrated yet
            pass
