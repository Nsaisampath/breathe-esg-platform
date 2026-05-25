"""
Django settings for breathe_esg project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

# In production, specify allowed hosts. In development, allow localhost.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if not DEBUG:
    # Production: Render provides the URL automatically
    # But also allow the production domain from environment
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',') if os.getenv('ALLOWED_HOSTS') else ['*']

# Installed apps - Django's modular system
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    
    # Our apps
    'apps.companies.apps.CompaniesConfig',
    'apps.uploads.apps.UploadsConfig',
    'apps.records.apps.RecordsConfig',
    'apps.audit.apps.AuditConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serves static files
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'breathe_esg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'breathe_esg.wsgi.application'

# Database - PostgreSQL connection
# In production, Render provides DATABASE_URL environment variable
# In development, we use individual DB environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Production: Use DATABASE_URL from Render
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # Development: Use individual database settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'breathe_esg'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, images)
# WhiteNoise will serve these in production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': ['rest_framework.filters.SearchFilter'],
}

# CORS - Allow frontend to call backend
# In development: Allow localhost:3000 (React dev server)
# In production: Will be configured via environment variable
if DEBUG:
    # Development: Allow React dev server
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
else:
    # Production: Allow specific frontend domain from environment
    # Example: CORS_ALLOWED_ORIGINS=https://breathe-esg.vercel.app
    cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
    if cors_origins:
        CORS_ALLOWED_ORIGINS = cors_origins.split(',')
    else:
        # Fallback: Allow all origins (not recommended for production)
        CORS_ALLOW_ALL_ORIGINS = True
