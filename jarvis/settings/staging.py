from jarvis.settings.base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': get_env_variable('DATABASE_ENGINE'),
        'NAME': get_env_variable('DATABASE_NAME'),
        'USER': get_env_variable('DATABASE_USER'),
        'PASSWORD': get_env_variable('DATABASE_PASSWORD'),
        'HOST': get_env_variable('HOST'),
        'PORT': '',
    }
}


ALLOWED_HOSTS = ['parser.psycho.com', 'parser.psycho.in']

# AWS S3 Storage
AWS_QUERYSTRING_AUTH = False
AWS_STORAGE_BUCKET_NAME = 'filters-api'
AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_FILE_OVERWRITE = False
MEDIAFILES_LOCATION = 'media/resumes/'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)

DEFAULT_FILE_STORAGE = "jarvis.custom_storage.MediaStorage"


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'filter-api <no-reply@psycho.com>'
EMAIL_HOST_USER = 'no-reply@psycho.com'
EMAIL_HOST_PASSWORD = get_env_variable('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

# Email Settings
ADMINS = (
  ('Anubhav', 'anubhavs286@gmail.com'),
  ('Anubhav722', 'anubhavdlostfrosty@gmail.com'),
)

