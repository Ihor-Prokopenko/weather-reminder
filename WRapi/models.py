from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    fullname = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.username}"


class Period(models.Model):
    interval = models.IntegerField()
    hours = models.CharField(max_length=255)

    def __str__(self):
        plural = "hour" if self.interval == 1 else "hours"
        return f"{self.interval} {plural}"

    def get_hours_list(self):
        return [int(hour) for hour in self.hours.split(',')]


class Location(models.Model):
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    actual_weather_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.city}, {self.country}"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='subscriptions')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='subscriptions')

    def __str__(self):
        return f"id({self.id}) | " \
               f"{self.user}({self.user.id}) | " \
               f"{self.location}({self.location.id}) |" \
               f" {self.period}({self.period.id})"

    def get_sub_info(self):
        return {
            'user': f"{self.user.username}",
            'location': f"{self.location.city}, {self.location.country}",
            'period': f"{self.period.interval} hours"
        }
