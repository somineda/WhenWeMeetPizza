import os
from celery import Celery

# 환경변수로 설정, 기본값은 development
django_env = os.environ.get('DJANGO_ENVIRONMENT', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{django_env}')

app = Celery('pizza')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
