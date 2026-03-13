import os
from pathlib import Path

# base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# load secret key from environment for production safety
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-9m41=63ocbpqkkqr*x_a2wl8wvyi9mx1j#5i=2@w(5jyqlx0ox'
)

# AGHU integration settings (all overridable via environment)
AGHU_BASE_URL = os.environ.get('AGHU_BASE_URL', 'http://aghu.hospital.gov.br')
AGHU_TIMEOUT = int(os.environ.get('AGHU_TIMEOUT', '10'))
AGHU_USE_DB = os.environ.get('AGHU_USE_DB', 'True').lower() in ('1', 'true', 'yes')

# details for the remote AGHU database (separate from the local 'default' DB)
AGHU_DB_NAME = os.environ.get('AGHU_DB_NAME', 'dbaghu')
AGHU_DB_USER = os.environ.get('AGHU_DB_USER', 'ugen_integra')
AGHU_DB_PASSWORD = os.environ.get('AGHU_DB_PASSWORD', 'aghuintegracao')
AGHU_DB_HOST = os.environ.get('AGHU_DB_HOST', '10.206.3.112')
AGHU_DB_PORT = os.environ.get('AGHU_DB_PORT', '6544')

# debug/hosts
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')
ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS', '127.0.0.1 localhost testserver'
).split()

# Apps instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'materiais',
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

ROOT_URLCONF = 'cme_qrcode.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # opcional, se quiser templates globais
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cme_qrcode.wsgi.application'

# Banco de dados principal da aplicação (PostgreSQL)
# the values are read from environment variables to avoid hardcoding
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'cme_qrcode'),
        'USER': os.environ.get('DB_USER', 'cme_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'cmehujbb123'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    },
}

# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Belem'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Arquivos de mídia (uploads, QR Codes, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Configurações de login/logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard_kit_paciente'   # após login, vai para o fluxo principal
LOGOUT_REDIRECT_URL = 'login'      # após logout, volta para login

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# during unit test runs we don't want to hit the real PostgreSQL server
# (and we may not have permission to create databases).  switch to an
# in‑memory SQLite database and disable AGHU lookups.
import sys
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    AGHU_USE_DB = False
