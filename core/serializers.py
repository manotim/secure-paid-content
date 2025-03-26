from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ Custom JWT Token Serializer to include user details in response """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        data.update({
            "id": user.id,
            "username": user.username,
            "role": getattr(user, "role", "client"),  # Ensure role is included
        })
        return data
