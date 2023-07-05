from django.forms import model_to_dict
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Subscription, Location, Period
from .serializers import UserSerializer, SubscriptionSerializer

from .weather_getter import get_weather


class UserAPIView(APIView):
    def get(self, request, pk=None):
        if not pk:
            users = User.objects.all()

            serializer = UserSerializer(users, many=True)

            return Response({'users': serializer.data})
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user)
        return Response({'user': serializer.data})


class SubscriptionsAPIView(APIView):
    def get(self, request, pk=None):
        if not pk:
            subscriptions = Subscription.objects.all()
            serializer = SubscriptionSerializer(subscriptions, many=True)

            return Response({'subscriptions': serializer.data})
        subscription = get_object_or_404(Subscription, id=pk)
        serializer = SubscriptionSerializer(subscription)

        return Response({'subscription': serializer.data})

    def post(self, request):
        request_data = {
            'user': User.objects.get(pk=request.data['user']),
            'location': Location.objects.get(pk=request.data['location']),
            'period': Period.objects.get(pk=request.data['period']),
        }
        new_subscription = Subscription.objects.create(
            user=request_data['user'],
            location=request_data['location'],
            period=request_data['period'],
        )

        return Response({'subscription': model_to_dict(new_subscription)})


class WeatherAPIView(APIView):
    def get(self, request, city=None):
        if not city:
            weather_data = get_weather('Lviv')
            return Response({'weather': weather_data})
        weather_data = get_weather(city)
        return Response({'weather': weather_data})


# class SubscriptionsAPIView(generics.ListAPIView):
#     queryset = Subscription.objects.all()
#     serializer_class = SubscriptionSerializer

