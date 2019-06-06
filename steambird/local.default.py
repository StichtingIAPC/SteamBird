# noinspection DuplicatedCode
import os

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.getenv('DB_NAME', 'stoomvogel'),
        'USER': os.getenv('DB_USERNAME', 'stoomvogel'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'stoomvogel'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
