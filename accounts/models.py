from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profile_picture = models.ImageField(upload_to="profile/", blank=True, null=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    is_doctor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_google = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    age = models.IntegerField(default=25)
    experience = models.CharField(max_length=50, null=True, blank=True)
    certificate_no = models.CharField(max_length=50, null=True, blank=True)
    fee_per_hour = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    phone = models.CharField(max_length=12, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Temp(models.Model):
    temp_id = models.CharField(max_length=100, primary_key=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    otp = models.CharField(max_length=6)

    def delete_after_delay(self, delay):
        def delete_temp():
            try:
                obj = Temp.objects.get(pk=self.pk)
                obj.delete()
                print(f'Temp object with ID {self.pk} has been deleted after {delay} seconds.')
            except ObjectDoesNotExist:
                print(f'Temp object with ID {self.pk} does not exist.')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Schedule the deletion of the Temp object after 3 minutes (180 seconds)
        self.delete_after_delay(200)
