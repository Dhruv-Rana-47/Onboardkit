# accounts/tables.py


import django_tables2 as tables
from .models import User,Role
from django.utils.safestring import mark_safe

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


class RoleTable(tables.Table):
    authorities = tables.Column(
        verbose_name='Authorities',
        orderable=False,
        attrs={
            "td": {
                "style": "width: 300px; height: 100px; overflow-y: auto; overflow-x: hidden; display: block; font-size: 0.9rem; white-space: normal;"
            },
            "th": {
                "style": "width: 150px;"
            }
        }
    )

    actions = tables.TemplateColumn(
        template_name='accounts/_role_actions.html',
        orderable=False
    )

    class Meta:
        model = Role
        template_name = "django_tables2/bootstrap5.html"
        fields = ('name', 'report_to', 'authorities', 'created_at')
        attrs = {'class': 'table table-striped table-hover'}

    def render_authorities(self, value):
        return mark_safe("<br>".join(str(auth) for auth in value.all()))

