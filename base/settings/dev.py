from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '16.170.224.110', '16.171.5.173', '172.31.35.218', '13.53.130.235', '172.31.32.59']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
