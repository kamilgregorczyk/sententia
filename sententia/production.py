from base import *
import psycopg2
SECRET_KEY = '6g@a7pu2g)+cg5@d8zh-mznfnk!r^_&n+%8l+cv+b+@ywz7&c!'

DEBUG = False
BASE_URL = 'http://sententia.uniqe15.usermd.net'
ALLOWED_HOSTS = ['sententia.uniqe15.usermd.net']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.environ.get('DB_USERNAME'),
        'NAME': os.environ.get('DB_USERNAME'),
        'PASSWORD': os.environ.get('PROJECT_DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
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
EMAIL_HOST_USER = 'sententia@uniqe15.usermd.net'
EMAIL_HOST_PASSWORD = '#Qwemelly24'
