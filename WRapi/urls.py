from django.urls import path, include

from . import views
from .scheduler import create_jobs
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path(
        'subscriptions/',
        include([
            path('', views.SubscriptionsAPIView.as_view(), name='subscriptions'),
            path('create/', views.SubscriptionsAPIView.as_view(), name='create_subscription'),
            path('<int:pk>/', views.SubscriptionsAPIView.as_view(), name='subscription_details'),
            path('<int:pk>/update/', views.SubscriptionsAPIView.as_view(), name='update_subscription'),
            path('<int:pk>/delete/', views.SubscriptionsAPIView.as_view(), name='delete_subscription'),
        ]),
    ),
    path(
        'auth/',
        include([
            path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
            path('register/', views.RegistrationAPIView.as_view(), name='register'),
        ])
    )
]

create_jobs()
