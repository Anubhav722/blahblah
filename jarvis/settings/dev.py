from jarvis.settings.base import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

INSTALLED_APPS += ('rest_framework_docs',)

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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

