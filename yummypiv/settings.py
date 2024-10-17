import os
from pathlib import Path
from services.utils import read_json

BASE_DIR = Path(__file__).resolve().parent.parent

# Load root conf env
root_env = read_json('root_conf.json')

# Project/Owner conf
APP_NAME = root_env['app_name']
APP_ALIAS_NAME = root_env['app_alias_name']
APP_INDEX_SUBTITLE = root_env['app_index_subtitle']
STORAGE_ALLOCATION = root_env['storage_allocation'] # unit storage MB
COMPANY_ADDRESS = root_env['contact_info']['company_address']
EMAIL = root_env['contact_info']['email']
PHONE_NUMBER = root_env['contact_info']['phone_number']

# Firebase conf
FIREBASE_CREDENTIALS = root_env['firebase_conf']['firebase_credentials']
FIREBASE_BUCKET_NAME = root_env['firebase_conf']['firebase_bucket_name']

# Mail server conf
MAIL_DOMAIN = root_env['mail_settings']['mail_domain']
MAIL_HOST = root_env['mail_settings']['mail_host']
SMTP_PORT = root_env['mail_settings']['smtp_port']
DEFAULT_MAIL_USERNAME = root_env['mail_settings']['default_mail_username']
DEFAULT_MAIL_PASSWORD = root_env['mail_settings']['default_mail_password']


CSRF_TRUSTED_ORIGINS = [
    'https://yummypiv.com',
    'http://yummypiv.com',
    'https://systema.id',
    'http://systema.id',
]

ALLOWED_HOSTS = root_env['web_settings']['allowed_host']

AUTH_USER_MODEL = 'apps.Users'

SECRET_KEY = 'django-insecure-i28tof6w9e6a@+6zq-#-s83(k0$708-n-q*hp1tj49!+czspaq'

DEBUG = root_env['web_settings']['debug']

INSTALLED_APPS = [
    'apps',
    'viewer',
    'services',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = root_env['web_settings']['root_urlconf']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['template'],
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

WSGI_APPLICATION = root_env['web_settings']['wsgi_application']


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# during development add this line
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
