from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    register,
    protected_view,
    upload_media,
    create_purchase
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", register, name="register"),
    path("protected/", protected_view, name="protected_view"),
    path("media/upload/", upload_media, name="upload_media"),
    path("purchase/", create_purchase, name="create_purchase"),
]
