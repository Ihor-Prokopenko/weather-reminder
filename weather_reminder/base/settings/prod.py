from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': 5432,
    }
}
