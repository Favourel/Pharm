from datetime import datetime

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin

from products.models import Checkout


# from products.models import Checkout

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    picture_url = models.ImageField(default='2placeholder_test_b9l9NT5.png', upload_to='profile_images')
    address = models.CharField(max_length=255, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=datetime.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        (1, "Account Created"), (2, "Order"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             related_name="noti_to_user")

    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    orders = models.ManyToManyField(Checkout, blank=True)

    date_posted = models.DateTimeField(default=datetime.now)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} notification'


class Prescription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             )
    text = models.TextField()
    document = models.FileField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} prescription"
