import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-development-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'admin_panel.apps.BotDataApp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'admin_panel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'admin_panel', 'templates')],
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

WSGI_APPLICATION = 'admin_panel.wsgi.application'

import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./bot_database.db')

if DATABASE_URL.startswith('postgresql'):

    django_url = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    parsed = urlparse(django_url)

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path[1:] if parsed.path else 'usn_bot_db',
            'USER': parsed.username or 'usn_bot',
            'PASSWORD': parsed.password or 'secure_password',
            'HOST': parsed.hostname or 'localhost',
            'PORT': parsed.port or 5432,
            'CONN_MAX_AGE': 600,
        }
    }
else:

    db_path = DATABASE_URL.replace('sqlite+aiosqlite:///', '').replace('sqlite:///', '').replace('sqlite:', '')
    if not db_path or db_path == './bot_database.db':
        db_path = 'bot_database.db'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, db_path if not db_path.startswith('/') else db_path.lstrip('/')),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'admin_panel', 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'admin_panel', 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'admin_panel', 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_SITE_HEADER = "USN Telegram Bot - Панель управления"
ADMIN_SITE_TITLE = "USN Admin"
ADMIN_SITE_URL = None
