# accounts/management/commands/init_authorities.py

from django.core.management.base import BaseCommand
from accounts.models import Authority

class Command(BaseCommand):
    help = 'Initialize default authorities'

    def handle(self, *args, **kwargs):
        default_authorities = [
            ("manage_roles", "Create, edit, delete roles"),
            ("manage_departments","create,edit,delete departments"),
            ("view_hierarchy","View Company Hierarchy"),
            ("manage_hierarchy", "Set up user hierarchy and mentor mapping"),
            ("create_user", "Create new user"),
            ("edit_user", "Edit user profile"),
            ("view_users", "View user list"),
            ("assign_user", "Assign user to role or mentor"),
            ("view_mentor_info", "View assigned mentor details"),
            ("view_subordinates", "View subordinates under hierarchy"),
            
            # Template & Task Authorities
            ("view_templates", "View onboarding templates"),
            ("create_template", "Create onboarding templates"),
            ("edit_template", "Edit templates"),
            ("assign_template", "Assign templates to users or roles"),
            ("create_task", "Create individual task"),
            ("assign_task", "Assign task to user"),
            ("edit_task", "Edit assigned task"),
            ("delete_task", "Delete or revoke a task"),
            ("view_tasks", "View assigned tasks"),
            ("complete_task", "Mark task as complete"),
            ("give_feedback", "Give feedback on task"),
            ("view_feedback", "View feedback"),

            # Progress, Reports, and Logs
            ("view_progress", "View progress reports"),
            ("export_reports", "Download/Export user performance reports"),
            ("rate_user", "Rate a user’s task performance"),
            ("view_logs", "View user activity logs"),

            # Messaging
            ("send_message", "Send direct message"),
            ("view_messages", "View received/sent messages"),

            # Admin Panel & Misc
            ("view_admin_dashboard", "View admin dashboard widgets"),
            ("view_own_dashboard", "View role-based dashboard widgets"),
        ]

        for code, label in default_authorities:
            Authority.objects.get_or_create(code=code, defaults={'label': label})

        self.stdout.write(self.style.SUCCESS("Authorities initialized successfully."))
