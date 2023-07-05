from django.contrib import admin
from .models import User, Subscription, Location, Period


admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(Location)
admin.site.register(Period)
