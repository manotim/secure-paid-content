from django.urls import path
from .views import CustomTokenObtainPairView, register, protected_view
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", register, name="register"),
    path("protected/", protected_view, name="protected_view"),
]
