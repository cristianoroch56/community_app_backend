from django.db import models
from authentication.models import User


class HelpAndSupport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Help and Support"

    def __str__(self):
        return f"Help and Support #{self.pk} status {self.status}"
