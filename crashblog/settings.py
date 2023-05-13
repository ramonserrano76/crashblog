"""
Django settings for crashblog project.
Generated by 'django-admin startproject' using Django 3.2.4.
For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Obtiene la ruta absoluta del archivo config.env


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9n_ih-bhy$#92@-+)%zuxw_jilauy2wg313@p2rq3#fxxm20u+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'registration',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'core',
    'blog',
    'ckeditor',
    'profiles',
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

ROOT_URLCONF = 'crashblog.urls'

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

DJRICHTEXTFIELD_CONFIG = {
    'js': ['//cdn.tiny.cloud/1/no-api-key/tinymce/5/tinymce.min.js'],
    'init_template': 'djrichtextfield/init/tinymce.js',
    'settings': {
        'menubar': False,
        'plugins': 'link image',
        'toolbar': 'bold italic | link image | removeformat',
        'width': 700
    }
}


WSGI_APPLICATION = 'crashblog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')
#auth redirects
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
DEFAULT_IMAGE_URL = 'https://demofree.sirv.com/nope-not-here.jpg'
# Cargar variables de entorno desde el archivo config.env
LINKEDIN_CLIENT_ID = '779t61pwcb1014'
LINKEDIN_CLIENT_SECRET = '5jaNbiMrjlR1aCzF'
CLIENT_ID = 'Njl1eG1MTkREM1J3UjVzWHBIRTc6MTpjaQ'
CLIENT_SECRET = 'LXd4FQxX0jVLarw8NStx4gtxGyHaXyk5uCpFxWv2xBHgRB1GhF'
CONSUMER_KEY = 'ogKdSKDeBi1oiUtB8LZCnYzkw'
CONSUMER_SECRET = 'XG2SKvAjLDUlnw8R8Ghbg747m7OS0SC0vapUmhsBYPFl94nuAM'
ACCESS_TOKEN = '1654219252013072384-PHEyxTdlmncmqy4p58v8uSmtxygMYn'
ACCESS_TOKEN_SECRET = 'wxCKaPSlaNIoNlw7fj1aPX1nrRPPSj0nK6k2Go0Fv0rId'
ACCESS_TOKEN_short = '578fb9e220945403aeb3941da1f6747060681a1c'

REDIRECT_URI = 'https://www.blogifyar.pro/redirect_uri/'
REDIRECT_URI_2 = "https%3A%2F%2Fwww.blogifyar.pro%2Fredirect_uri2%2F"
REDIRECT_URI_3 = "https://www.blogifyar.pro/redirect_uri2/"
# EMAIL
#emails
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")
else:
#aquí hay que configurar un mail real para producción
#   pass
# #email config
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_USE_TLS = False
    EMAIL_PORT = 587
    EMAIL_USE_SSL = True
    EMAIL_HOST_USER = 'proyectodjangoblog1@gmail.com'
    EMAIL_HOST_PASSWORD = 'auscoftkettyqulr'
    DEFAULT_FROM_EMAIL = 'proyectodjangoblog1@gmail.com'
    SESSION_ENGINE = 'django.contrib.sessions.backends.file'
    # EMAIL_HOST = 'SMTP.MAIL.RU'
    # EMAIL_HOST_USER = 'proyectodjangoblog@mail.ru'
    # EMAIL_HOST_PASSWORD = 'ProyectoCaC'
    # EMAIL_PORT = '465'


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
