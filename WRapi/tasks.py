from celery.schedules import crontab

from WRapi.mail_sender import notify_new_subscription
from celery import shared_task
from WRapi.notificator import send_mails

from WRapi.models import Period
from base.celery import app


@shared_task
def notify_about_subscription(notify_body):
    notify_new_subscription(notify_body)

    return f"New sub: {notify_body.get('email')} | {notify_body.get('city')}, {notify_body.get('country')} " \
           f"| {notify_body.get('period')}"


@app.task
def send_mails_task(per):
    send_mails(per)


periods = Period.objects.all().order_by('interval')
beat_schedule = {}

if periods:
    for period in periods:
        beat_schedule[period.__str__()] = {
            'task': 'WRapi.tasks.send_mails_task',
            'schedule': crontab(hour=period.hours, minute='0'),
            'args': (int(period.interval),),
        }

app.conf.beat_schedule = beat_schedule
