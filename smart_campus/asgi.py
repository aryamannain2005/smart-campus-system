"""
ASGI config for Smart Campus Management System.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_campus.settings')
application = get_asgi_application()
