import requests
from django.urls import path
from django.db.models import Q
from .models import Subscription, Location, Period

from base.settings.base import WEATHER_API_KEY, WEATHER_API_BASE_URL


def get_weather(city):
    api_key = WEATHER_API_KEY
    base_url = WEATHER_API_BASE_URL
    params = {
        'key': api_key,
        'q': city,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        return None


def get_locations(period: int = None):
    intervals = [period.interval for period in Period.objects.all().order_by('interval')]
    if period in intervals:
        locations = None
        for interval in intervals:
            period_obj = Period.objects.get(interval=interval)
            period_locations = Location.objects.filter(subscriptions__period=period_obj)
            if not locations:
                locations = period_locations
            else:
                locations.union(period_locations)
            if interval == period:
                break
        return locations


def update_weather_data(interval=None):
    locations = get_locations(period=6)
    for location in locations:
        city = location.city
        weather_data = get_weather(city)
        if weather_data:
            actual_weather_data = {
                'city': weather_data['location']['name'],
                'region': weather_data['location']['region'],
                'country': weather_data['location']['country'],
                'last_updated': weather_data['current']['last_updated'],
                'temperature': weather_data['current']['temp_c'],
                'condition': weather_data['current']['condition']['text'],
                'wind': weather_data['current']['wind_mph'],
            }
            location.actual_weather = actual_weather_data
            location.save()
