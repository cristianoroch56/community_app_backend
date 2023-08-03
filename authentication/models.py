from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import binascii
import os

User = settings.AUTH_USER_MODEL


# Create your models here.
class ActivationOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Activation OTP {self.otp} for {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.id:
            # Set the expiration time to 5 minutes from the current time
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)


class ForgetPasswordOtp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP {self.otp} for {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.id:
            # Set the expiration time to 5 minutes from the current time
            self.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)


class ForgetPasswordToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()

    class Meta:
        verbose_name = "Forget Password Token"
        verbose_name_plural = "Forget Password Tokens"


class User(AbstractUser):
    parent_id = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    online = models.BooleanField(null=True, blank=True)
    country_code = models.IntegerField(null=True, blank=True)
    country_flag = models.CharField(null=True, blank=True, max_length=50)
    current_thread_id = models.IntegerField(blank=True, null=True)

    # Add any additional fields or methods you need

    def __str__(self):
        return self.username
