import psycopg2

from base import *

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False
BASE_URL = 'https://sententiaup.pl'
ALLOWED_HOSTS = ['sententiaup.pl', 'www.sententiaup.pl', 'sententia.uniqe15.usermd.net']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.environ.get('DB_USERNAME'),
        'NAME': os.environ.get('DB_USERNAME'),
        'PASSWORD': os.environ.get('PROJECT_DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'OPTIONS': {
            'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
        }
    }
}

ENV_PATH = os.path.abspath(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(ENV_PATH, '../public/static/')
MEDIA_ROOT = os.path.join(ENV_PATH, '../public/media/')

ADMINS = [('Kamil', 'gregorczyk@me.com')]
EMAIL_USE_TLS = True
EMAIL_HOST = 'mail8.mydevil.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'admin@sententiaup.pl'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

CACHES = {
    'default': {
        'BACKEND': 'poll.memcached.LargeMemcachedCache',
        'LOCATION': '127.0.0.1:11223',
    }
}
