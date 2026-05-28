import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholarship_portal.settings')
django.setup()

from django.contrib.auth.models import User

try:
    User.objects.get(username='admin')
    print('Admin user already exists.')
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'admin@example.com', 'AdminPass123!')
    print('Admin superuser created successfully.')
