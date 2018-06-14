from jarvis.settings.base import *

DEBUG = True

# Not using because of the conflicts with JSONField() in Visitor

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

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

INSTALLED_APPS += ('django_nose', 'test_without_migrations')

TESTDATA_DIRS = os.path.dirname(BASE_DIR) + '/testdata/'
# Running Django Test on memory
if 'test' in sys.argv:
    DATABASE_ENGINE = 'sqlite3'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_URL = '/test_upload/'

MEDIA_ROOT = BASE_DIR + '/test_files/'

TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package= skill, accounts, resume',
    '--with-doctest',
    '--verbosity=2',
    '--with-xunit',
    '--xunit-file=xunittest.xml',
    '--cover-xml',
    '--cover-xml-file=coverage.xml',
    # '--omit=../*migrations*'
    # '--cover-omit=*/migrations/*',
    # '--noexe',
    # 'ignore-files = *migrations*'
]
