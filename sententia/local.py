import psycopg2
from base import *

SECRET_KEY = '6g@a7pu2g)+cg5@d8zh-mznfnk!r^_&n+%8l+cv+b+@ywz7&c!'

DEBUG = True
BASE_URL = 'http://localhost:8000'
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'postgres',
        'NAME': 'sententia',
        'PASSWORD': 'online13',
        'HOST': 'localhost',
        'PORT': '5433',
        'OPTIONS': {
            'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
        },

    }
}

STATIC_ROOT = ''

