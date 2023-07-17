import os
from celery import Celery, shared_task
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings.dev')

app = Celery('base')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print('Hello from debug print')

    return 'Hello from debug return'