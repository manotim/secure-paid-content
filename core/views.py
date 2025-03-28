from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model, authenticate,  authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer, PurchaseSerializer, MediaUploadSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from cloudinary.uploader import upload
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .permissions import IsMerchant
from .serializers import MediaFileSerializer

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    role = request.data.get("role", "client")  # Default role is client

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, role=role)
    
    # Generate JWT Tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        },
    }, status=status.HTTP_201_CREATED)


# ✅ Login User and Get JWT Token
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    # Generate JWT Tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        },
    }, status=status.HTTP_200_OK)


# ✅ Protected Route (Example)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def protected_view(request):
    return Response({"message": "This is a protected route. You are authenticated!"})


# ✅ Media Upload API
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_media(request):
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        upload_result = upload(file)
        return Response({"url": upload_result["secure_url"]}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ✅ Purchase API
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_purchase(request):
    serializer = PurchaseSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        purchase = serializer.save(user=request.user)
        return Response({"message": "Purchase successful", "purchase_id": purchase.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsMerchant])
def add_product(request):
    """
    Allows a merchant (creator) to add a media product (image or audio).
    """
    serializer = MediaFileSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save(creator=request.user)  # Assign logged-in user as the creator
        return Response({"message": "Product added successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

