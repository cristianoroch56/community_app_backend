from django.db import models
from django.conf import settings
from authentication.models import User
from services.notifications import create_notification


# Create your models here.
class Events(models.Model):
    event_name = models.CharField(max_length=255)
    event_content = models.TextField()
    location = models.CharField(max_length=255)
    event_image = models.ImageField(
        upload_to=f"{settings.AWS_BASE_UPLOAD_PATH}/event_images"
    )
    event_date = models.DateTimeField(null=True, blank=True)
    event_duration = models.DateTimeField(null=True, blank=True)
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_events')
    bookmarked_by = models.ManyToManyField(User, blank=True, related_name='bookmarked_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Events"
        verbose_name_plural = "Events"

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if it's a new Event instance

        # Call the original save method
        super().save(*args, **kwargs)

        if is_new:
            user_obj = User.objects.all()
            # Create a notification
            title = "The Latest Event Unveiled"
            content = self.event_name

            for user in user_obj:
                # Call the create_notification function to create and send the notification
                create_notification(user=user, title=title, content=content, content_id=self.id)
