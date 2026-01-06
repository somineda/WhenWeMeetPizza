import os

# Default to development settings if DJANGO_SETTINGS_MODULE is not set
env = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if env == 'production':
    from .production import *
else:
    from .development import *
