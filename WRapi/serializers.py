from rest_framework import serializers
from .models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'user', 'location', 'period')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['info'] = instance.get_str_info()
        return representation

