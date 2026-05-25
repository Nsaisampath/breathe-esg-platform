"""
WSGI config for breathe_esg project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breathe_esg.settings')
application = get_wsgi_application()
