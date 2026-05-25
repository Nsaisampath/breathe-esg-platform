import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breathe_esg.settings')
django.setup()

from apps.companies.models import Company

company, created = Company.objects.get_or_create(name="Test Company")
print(f"✓ Company ID: {company.id}")
print(f"✓ Company Name: {company.name}")
print(f"✓ Created: {created}")
