from django.urls import path, include

from . import views
from rest_framework_simplejwt import views as jwt_views

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.utils import swagger_auto_schema


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for Weather Reminder",
    ),
    public=True,
)

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
    ),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
