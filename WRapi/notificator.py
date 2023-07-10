from .models import Subscription, Location, Period
from django.db.models import Q

from .weather_getter import get_weather


def get_locations(intervals: list = None):
    if not intervals:
        return None
    locations = None
    for elem in intervals:
        period_obj = Period.objects.get(interval=elem)
        period_locations = Location.objects.filter(subscriptions__period=period_obj)
        if not locations:
            locations = period_locations
        else:
            locations = locations.union(period_locations)
    return locations


def get_subscriptions(intervals: list = None):
    if not intervals:
        return None
    subscriptions = None
    for elem in intervals:
        subscriptions_set = Subscription.objects.filter(period__interval=elem)
        if not subscriptions:
            subscriptions = subscriptions_set
        else:
            subscriptions = subscriptions.union(subscriptions_set)
    return subscriptions


def update_weather_data(locations=None):
    if not locations:
        return None
    for location in locations:
        city = location.city
        weather_data = get_weather(city)
        try:
            actual_weather_data = {
                'city': weather_data['location']['name'],
                'region': weather_data['location']['region'],
                'country': weather_data['location']['country'],
                'last_updated': weather_data['current']['last_updated'],
                'temperature': weather_data['current']['temp_c'],
                'condition': weather_data['current']['condition']['text'],
                'wind': weather_data['current']['wind_mph'],
            }
            location.actual_weather_data = actual_weather_data
            location.save()
        except KeyError:
            print(f"Something went wrong to update weather in {city}")


def get_mail_data(period: int = None) -> dict:
    intervals = [p.interval for p in Period.objects.all().order_by('interval') if p.interval <= period]

    locations = get_locations(intervals)
    update_weather_data(locations)

    subscriptions = get_subscriptions(intervals)

    mails_data = {sub.id: {"email": sub.user.email,
                           "weather": sub.location.actual_weather_data} for sub in subscriptions}

    return mails_data


def send_mails(period: int = None):
    mails_data = get_mail_data(period)
    data = [(mails_data[mail]['email'], mails_data[mail]['weather']['city']) for mail in mails_data]
