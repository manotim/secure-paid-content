from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer  # Import your serializer
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """ Custom JWT Login Response """
    serializer_class = CustomTokenObtainPairSerializer  # Use the custom serializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.user  # Extract the user instance from the serializer
        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        return Response({
            "access": access,
            "refresh": refresh,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": getattr(user, "role", "client"),  # Use getattr to avoid AttributeError
            },
        })

@api_view(["POST"])
def register(request):
    """ Register New User """
    username = request.data.get("username")
    password = request.data.get("password")
    role = request.data.get("role", "client")  # Default role

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    
    # Set the role if it exists in the user model
    if hasattr(user, "role"):
        user.role = role
        user.save()

    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "username": user.username,
            "role": getattr(user, "role", "client"),  # Handle missing role attribute
        },
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    print(f"Authenticated User: {request.user}")  # Debugging line
    return Response({"message": "This is a protected route. You are authenticated!"})