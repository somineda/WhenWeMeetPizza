from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Security settings (HTTPS 사용 시 True로 변경)
USE_HTTPS = os.environ.get('USE_HTTPS', 'False').lower() == 'true'
SECURE_SSL_REDIRECT = USE_HTTPS
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Use real email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# CORS for production
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in
    os.environ.get('CORS_ALLOWED_ORIGINS', FRONTEND_URL).split(',')
]
CORS_ALLOW_CREDENTIALS = True

# Celery Beat settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
