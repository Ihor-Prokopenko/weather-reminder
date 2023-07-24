from datetime import timedelta
from pathlib import Path
import os
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wrapi_postgres',
        'USER': 'wrapi_user',
        'PASSWORD': 'wrapi_password',
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': 5432,
    }
}
