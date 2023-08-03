from django.db import models
from authentication.models import User
from django.conf import settings


class UserProfile(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    email = models.EmailField(null=True)
    profile_pic = models.ImageField(
        upload_to=f"{settings.AWS_BASE_UPLOAD_PATH}/profile_pics", null=True
    )
    relation_with_main_member = models.CharField(max_length=100, null=True)
    birthdate = models.DateField(null=True)
    education = models.CharField(max_length=100, null=True)
    marital_status = models.BooleanField(null=True)
    currently_living_at = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    push_notification = models.BooleanField(null=True, default=True)

    def __str__(self):
        return f"Profile of {self.user.username} and name is {self.user.first_name} {self.user.last_name}"
