from django.db import models
from django.conf import settings
from services.notifications import create_notification
from authentication.models import User


# Create your models here.
class News(models.Model):
    news_content = models.TextField()
    news_title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=f"{settings.AWS_BASE_UPLOAD_PATH}/news_images")
    is_reported = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if it's a new News instance

        # Call the original save method
        super().save(*args, **kwargs)

        if is_new:
            user_obj = User.objects.all()
            # Create a notification
            title = "New news Arrived"
            content = self.news_title

            for user in user_obj:
                # Call the create_notification function to create and send the notification
                create_notification(user=user, title=title, content=content, content_id=self.id)
