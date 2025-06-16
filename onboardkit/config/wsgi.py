"""
WSGI config for onboardkit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application
from django.db import OperationalError, connection
from django.contrib.auth import get_user_model
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

User = get_user_model()

try:
    # Apply migrations on startup (only first time)
    from django.core.management import call_command
    call_command('migrate', interactive=False)

    # Check if table exists before querying
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('public.accounts_user');")
        result = cursor.fetchone()[0]

    if result and not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
        print("✅ Admin user created.")

except OperationalError as e:
    print(f"[WARNING] Skipping user creation due to DB error: {e}")

application = get_wsgi_application()
