from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth import get_user_model

class User(AbstractUser):
    ROLE_CHOICES = (
        ('creator', 'Creator'),
        ('client', 'Client'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    groups = models.ManyToManyField(Group, related_name="core_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="core_user_permissions", blank=True)

class MediaFile(models.Model):
    MEDIA_TYPES = (
        ('audio', 'Audio'),
        ('image', 'Image'),
    )

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='media/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_files')
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)  # Visibility control



User = get_user_model()

class Purchase(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    
    PAYMENT_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    media = models.ForeignKey(MediaFile, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default=STATUS_PENDING
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['client']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['purchased_at']),
        ]

    def __str__(self):
        return f"{self.client.username} - {self.media} - {self.amount_paid} - {self.payment_status}"

    
