from django.db import models
from authentication.models import User


# Create your models here.
class SendNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(null=True, blank=True, max_length=100)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    content_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
