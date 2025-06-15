# accounts/tables.py


import django_tables2 as tables
from .models import User

class UserTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='accounts/_user_actions.html',
        orderable=False
    )

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap5.html"
        fields = ('username', 'email', 'role', 'is_active', 'date_joined')
        attrs = {'class': 'table table-striped table-hover'}