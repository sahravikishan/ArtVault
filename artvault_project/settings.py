"""
Django settings for artvault_project project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-artvault-secret-key-change-in-production-2024'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'artists',
    'paintings',
    'accounts',
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

ROOT_URLCONF = 'artvault_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'artvault_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'   # IST
USE_I18N = True
USE_TZ   = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Payment Gateway (Razorpay) ────────────────────────────────────
RAZORPAY_KEY_ID     = os.environ.get('RAZORPAY_KEY_ID',     'rzp_test_placeholder_key')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'placeholder_secret')

# ── Email Configuration ───────────────────────────────────────────
# In development, emails are printed to the terminal console.
# For production, switch to SMTP by setting EMAIL_BACKEND to
#   'django.core.mail.backends.smtp.EmailBackend'
# and supply the env vars below.
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'   # dev default
)
EMAIL_HOST          = os.environ.get('EMAIL_HOST',          'smtp.gmail.com')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT',      '587'))
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER',     '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL',  'ArtVault <noreply@artvault.in>')
ARTVAULT_ADMIN_EMAIL = os.environ.get('ARTVAULT_ADMIN_EMAIL', EMAIL_HOST_USER)
