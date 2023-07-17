from django.core.mail import send_mail

from base.settings.base import EMAIL_HOST_USER


def send_weather(email, username, weather_data):
    email_from = EMAIL_HOST_USER
    email_to = [email]
    subject = "Your weather!"

    city = f"{weather_data.get('city')}"
    region = f", {weather_data.get('region')}" if weather_data.get('region') else ''
    country = f", {weather_data.get('country')}" if weather_data.get('country') else ''
    temperature = f"temperature - {weather_data.get('temperature')}"
    condition = f"condition - {weather_data.get('condition')}"
    wind = f"wind - {weather_data.get('wind')}"
    last_updated = f"Actual on {weather_data.get('last_updated')}"

    message = f"Hello {username}! Here is your weather in {city}{region}{country}: \n\n" \
              f"{temperature}\n" \
              f"{condition}\n" \
              f"{wind}\n" \
              f"{last_updated}\n"

    send_mail(subject, message=message, from_email=email_from, recipient_list=email_to)

    return True


def notify_new_subscription(notify_body):
    email_from = EMAIL_HOST_USER
    email_to = [notify_body.get('email')]
    subject = "New subscription!"

    plural = 'hour' if notify_body.get('period') == 1 else 'hours'

    message = f"Hello {notify_body.get('username')}! " \
              f"You just subscribed on weather notification in " \
              f"{notify_body.get('city')}, {notify_body.get('country')} " \
              f"for every {notify_body.get('period')} {plural}!"

    send_mail(subject, message=message, from_email=email_from, recipient_list=email_to)

    return True
