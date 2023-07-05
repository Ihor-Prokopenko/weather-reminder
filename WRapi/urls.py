from django.urls import path, include

from . import views
from .scheduler import create_jobs

urlpatterns = [
    path(
        'users/',
        include([
            path('', views.UserAPIView.as_view(), name='user_list'),
            path('<int:pk>', views.UserAPIView.as_view(), name='user_list'),
        ])),
    path(
        'subscriptions/',
        include([
            path('', views.SubscriptionsAPIView.as_view(), name='subscriptions'),
            path('<int:pk>/', views.SubscriptionsAPIView.as_view(), name='subscriptions'),
        ]),
    ),
    path(
        'get_weather/',
        include([
            path('', views.WeatherAPIView.as_view(), name='get_weather'),
            path('<str:city>/', views.WeatherAPIView.as_view(), name='get_weather'),
        ])
    )
]

create_jobs()
