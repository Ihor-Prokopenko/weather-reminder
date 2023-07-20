from datetime import timedelta

from django.db.models import Q
from django.forms import model_to_dict
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from .tasks import notify_new_subscription, get_weather

from .models import User, Subscription, Location, Period
from .serializers import UserSerializer, SubscriptionSerializer


def get_or_create_location(city):
    weather_data = get_weather(city)
    if not weather_data:
        return None
    location = Location.objects.filter(Q(city__iexact=city)).first()
    if location:
        return location
    response_city = weather_data.get('location', {}).get('name')
    if not response_city:
        return None
    location = Location.objects.create(city=response_city,
                                       country=weather_data.get('location', {}).get('country'))
    if not location:
        return None

    return location


class SubscriptionsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        if not pk:
            subscriptions = request.user.subscriptions.all()
            serializer = SubscriptionSerializer(subscriptions, many=True)

            return Response({'subscriptions': serializer.data})
        subscription = Subscription.objects.filter(id=pk).first()
        if not subscription:
            return Response({'message': f'Subscription with id({pk}) not found!'},
                            status=status.HTTP_404_NOT_FOUND)
        if subscription.user.id != request.user.id:
            return Response({'message': 'Unauthorized access...'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = SubscriptionSerializer(subscription)

        return Response({'subscription': serializer.data})

    def post(self, request, pk=None):
        city = request.data.get('location')
        period = request.data.get('period')
        if not city:
            return Response({'message': "Location is a required argument..."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not period:
            return Response({'message': "Period is a required argument..."},
                            status=status.HTTP_400_BAD_REQUEST)
        period_obj = Period.objects.filter(interval=request.data['period']).first()
        if not period_obj:
            periods = [period.interval for period in Period.objects.all()]
            return Response({'message': f"Unsupported period {request.data['period']}",
                             'available_periods': periods}, status=status.HTTP_400_BAD_REQUEST)
        location_obj = get_or_create_location(city)

        if not location_obj:
            return Response({'message': f"Unsupported location '{request.data['location']}'"},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(pk=request.user.id)
        new_subscription = Subscription.objects.create(
            user=user,
            location=location_obj,
            period=period_obj,
        )
        if not new_subscription:
            return Response({'message': 'There was an error creating subscription...'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        notify_body = {
            'email': user.email,
            'username': user.username,
            'city': location_obj.city,
            'country': location_obj.country,
            'period': period_obj.interval,
        }
        notify_new_subscription.delay(notify_body)

        serializer = SubscriptionSerializer(new_subscription)
        return Response({'subscription': serializer.data})

    def patch(self, request, pk=None):
        subscription = Subscription.objects.filter(id=pk).first()
        if not subscription:
            return Response({'message': f'Subscription with id({pk}) not found!'},
                            status=status.HTTP_404_NOT_FOUND)
        if subscription.user.id != request.user.id:
            return Response({'message': 'Unauthorized access...'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'location' in request.data:
            location_obj = get_or_create_location(request.data['location'])
            if not location_obj:
                return Response({'message': f"Unsupported location '{request.data['location']}'"},
                                status=status.HTTP_400_BAD_REQUEST)
            subscription.location = location_obj

        if 'period' in request.data:
            period_obj = Period.objects.filter(interval=request.data['period']).first()
            if not period_obj:
                periods = [period.interval for period in Period.objects.all()]
                return Response({'message': f"Unsupported period {request.data['period']}",
                                 'available_periods': periods}, status=status.HTTP_400_BAD_REQUEST)
            subscription.period = period_obj

        subscription.save()

        serializer = SubscriptionSerializer(subscription)
        return Response({'subscription': serializer.data})

    def delete(self, request, pk=None):
        subscription = Subscription.objects.filter(id=pk).first()
        if not subscription:
            return Response({'message': f'Subscription with id({pk}) not found!'},
                            status=status.HTTP_404_NOT_FOUND)
        if subscription.user.id != request.user.id:
            return Response({'message': 'Unauthorized access...'}, status=status.HTTP_401_UNAUTHORIZED)
        subscription.delete()
        check_subscription = Subscription.objects.filter(id=pk).first()
        if not check_subscription:
            return Response({'message': f'Subscription with id({pk}) deleted successfully!'},
                            status=status.HTTP_204_NO_CONTENT)


class RegistrationAPIView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({'message': "Registration successful!",
                         'user_info': f"{user.username}, {user.email}"}, status=status.HTTP_201_CREATED)
