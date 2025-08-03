import django_tables2 as tables
from .models import User, Role
from django.utils.safestring import mark_safe

class UserTable(tables.Table):
    full_name = tables.Column(
        accessor='get_full_name',
        verbose_name='Full Name',
        order_by=('first_name', 'last_name')
    )

    department = tables.Column(
        accessor='department.name',
        verbose_name='Department',
        default='—'
    )

    company = tables.Column(
        accessor='company.name',
        verbose_name='Company',
        visible=False  # Hide since we're filtering by company already
    )

    role = tables.Column(
        accessor='role.name',
        verbose_name='Role'
    )

    mentor = tables.Column(
        accessor='mentor.get_full_name',
        verbose_name='Reports To',
        default='—'
    )

    status = tables.Column(
        accessor='is_active',
        verbose_name='Status',
        order_by=('is_active',),
        attrs={
            "td": {"class": "text-center"}
        }
    )

    actions = tables.TemplateColumn(
        template_name='accounts/_user_actions.html',
        orderable=False,
        attrs={
            "td": {"class": "text-end"}
        }
    )

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap5.html"
        fields = ('username', 'full_name', 'email', 'department', 'role', 'mentor', 'status', 'date_joined')
        attrs = {
            'class': 'table table-striped table-hover',
            'thead': {'class': 'table-light'}
        }

    def render_status(self, value):
        return mark_safe(
            f'<span class="badge bg-{"success" if value else "danger"}">'
            f'{"Active" if value else "Inactive"}'
            '</span>'
        )

class RoleTable(tables.Table):
    name = tables.Column(
        
        attrs={
            "a": {"class": "text-decoration-none"}
        }
    )

    report_to = tables.Column(
        accessor='report_to.name',
        verbose_name='Reports To',
        default='—'  # Shows em dash when empty
    )

    authorities = tables.Column(
        verbose_name='Authorities',
        orderable=False,
        attrs={
            "td": {
                "style": "max-width: 300px;",
                "class": "small"
            }
        }
    )

    created_at = tables.DateTimeColumn(
        format='M j, Y',
        verbose_name='Created'
    )

    actions = tables.TemplateColumn(
        template_name='accounts/_role_actions.html',
        orderable=False,
        attrs={
            "td": {"class": "text-end"}
        }
    )

    class Meta:
        model = Role
        template_name = "django_tables2/bootstrap5.html"
        fields = ('name', 'report_to', 'authorities', 'created_at')
        attrs = {
            'class': 'table table-striped table-hover',
            'thead': {'class': 'table-light'}
        }

    
    def render_authorities(self, value):
        if not value.exists():
            return mark_safe('<span class="text-muted">No authorities</span>')

        return mark_safe(
            """
            <div style="max-height: 100px; overflow-y: auto; padding-right: 5px;">
                <ul class='mb-0 ps-3'>
                    {}
                </ul>
            </div>
            """.format("".join(f"<li>{auth.label}</li>" for auth in value.all()))
        )

    
