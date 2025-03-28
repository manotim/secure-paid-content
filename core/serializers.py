from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MediaFile, Purchase
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Add custom fields to the token response
        data['id'] = user.id
        data['username'] = user.username
        data['role'] = user.role  # Assuming `role` is a field in your User model

        return data


# ✅ User Registration Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# ✅ Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# ✅ Media Upload Serializer
class MediaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = ['id', 'title', 'file', 'media_type', 'price', 'is_published', 'creator']
        read_only_fields = ['creator']

# ✅ Media Upload Serializer (For File Uploads)
class MediaUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

# ✅ Updated Purchase Serializer
class PurchaseSerializer(serializers.ModelSerializer):
    transaction_id = serializers.CharField(required=False, read_only=True)  # Ensure transaction_id is included
    media_price = serializers.DecimalField(source='media.price', max_digits=10, decimal_places=2, read_only=True)  # Show media price

    class Meta:
        model = Purchase
        fields = ['id', 'client', 'media', 'amount_paid', 'payment_status', 'transaction_id', 'purchased_at', 'media_price']
        read_only_fields = ['client', 'payment_status', 'transaction_id', 'purchased_at']

    def validate(self, data):
        """
        Ensure amount_paid matches the price of the media.
        """
        media = data.get('media')
        amount_paid = data.get('amount_paid')

        if media and amount_paid:
            if amount_paid != media.price:
                raise serializers.ValidationError({'amount_paid': "Amount must match the media price."})

        return data

    def create(self, validated_data):
        """
        Automatically set the client from the request user and generate a transaction_id.
        """
        request = self.context.get('request')
        user = request.user if request else None

        validated_data['client'] = user  # Set client to the authenticated user
        validated_data['transaction_id'] = f"TXN-{user.id}-{validated_data['media'].id}"  # Generate transaction ID

        return super().create(validated_data)
