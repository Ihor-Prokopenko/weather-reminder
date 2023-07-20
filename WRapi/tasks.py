import requests

from celery import shared_task
from celery.schedules import crontab
from django.core.mail import send_mail

from WRapi.models import Period, Location, Subscription
from base.celery import app
from base.settings.base import WEATHER_API_KEY, WEATHER_API_BASE_URL, EMAIL_HOST_USER


class PeriodDataContainer:
    def __init__(self, interval: int):
        self.interval = interval
        self.existing_intervals = [period.interval for period in Period.objects.all().order_by('interval')]
        if self.interval not in self.existing_intervals:
            self.is_valid = False
            return
        self.locations = self.get_locations()
        self.subscriptions = self.get_subscriptions()
        self.is_valid = True

    def get_locations(self):
        locations = None
        for interval in self.existing_intervals:
            period_obj = Period.objects.get(interval=interval)
            period_locations = Location.objects.filter(subscriptions__period=period_obj)
            if not locations:
                locations = period_locations
            else:
                locations.union(period_locations)
            if interval == self.interval:
                break
        return locations

    def get_subscriptions(self):
        subscriptions = None
        for interval in self.existing_intervals:
            subscriptions_set = Subscription.objects.filter(period__interval=interval)
            if not subscriptions:
                subscriptions = subscriptions_set
            else:
                subscriptions = subscriptions.union(subscriptions_set)
            if interval == self.interval:
                break
        return subscriptions


@shared_task
def get_weather(city):
    api_key = WEATHER_API_KEY
    base_url = WEATHER_API_BASE_URL
    params = {
        'key': api_key,
        'q': city,
    }

    response = requests.get(base_url, params=params)

    if not response.status_code == 200:
        return None
    weather_data = response.json()
    return weather_data


@shared_task
def update_weather(location_id):
    location = Location.objects.get(id=location_id)
    weather_data = get_weather(location.city)
    if not weather_data:
        return False
    actual_weather_data = {
        'city': weather_data.get('location').get('name'),
        'region': weather_data.get('location').get('region'),
        'country': weather_data.get('location').get('country'),
        'last_updated': weather_data.get('current').get('last_updated'),
        'temperature': weather_data.get('current').get('temp_c'),
        'condition': weather_data.get('current').get('condition').get('text'),
        'wind': weather_data.get('current').get('wind_mph'),
    }
    location.actual_weather_data = actual_weather_data
    location.save()

    return True


@shared_task
def send_weather(subscription_id):
    subscription_obj = Subscription.objects.get(id=subscription_id)
    if not subscription_obj:
        return False

    email_from = EMAIL_HOST_USER
    email_to = [subscription_obj.user.email]
    subject = "Your weather!"

    weather_data = subscription_obj.location.actual_weather_data
    city = f"{weather_data.get('city')}"
    region = f", {weather_data.get('region')}" if weather_data.get('region') else ''
    country = f", {weather_data.get('country')}" if weather_data.get('country') else ''
    temperature = f"temperature - {weather_data.get('temperature')}"
    condition = f"condition - {weather_data.get('condition')}"
    wind = f"wind - {weather_data.get('wind')}"
    last_updated = f"Actual on {weather_data.get('last_updated')}"

    message = f"Hello {subscription_obj.user.username}! Here is your weather in {city}{region}{country}: \n\n" \
              f"{temperature}\n" \
              f"{condition}\n" \
              f"{wind}\n" \
              f"{last_updated}\n"

    sent = send_mail(subject, message=message, from_email=email_from, recipient_list=email_to)
    if not sent:
        return False

    return True


@shared_task
def notify_new_subscription(notify_body):
    email_from = EMAIL_HOST_USER
    email_to = [notify_body.get('email')]
    subject = "New subscription!"

    plural = 'hour' if notify_body.get('period') == 1 else 'hours'

    message = f"Hello {notify_body.get('username')}! " \
              f"You just subscribed on weather notification in " \
              f"{notify_body.get('city')}, {notify_body.get('country')} " \
              f"for every {notify_body.get('period')} {plural}!"

    sent = send_mail(subject, message=message, from_email=email_from, recipient_list=email_to)
    if not sent:
        return False

    return True


@app.task
def notify_by_interval(interval):
    period_data = PeriodDataContainer(interval=interval)

    if not period_data.is_valid:
        return f"{interval} interval does not exist..."

    for location in period_data.locations:              # passed location id because celery
        update_weather.delay(location.id)               # does not send QuerySet as argument

    for subscription in period_data.subscriptions:
        send_weather.delay(subscription.id)

    return True


def get_beat_schedule():
    periods = Period.objects.all().order_by('interval')

    beat_schedule = {}
    for period in periods:
        beat_schedule[period.__str__()] = {
            'task': 'WRapi.tasks.notify_by_interval',
            'schedule': crontab(hour=period.hours, minute='44'),
            'args': (int(period.interval),),
        }

    return beat_schedule


app.conf.beat_schedule = get_beat_schedule()
