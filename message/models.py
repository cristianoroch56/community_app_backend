from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Q

# get the user model for the current Django project
User = get_user_model()


# Define a custom manager for the Thread model
class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        # Retrieve the user parameter from the kwargs, means it get user who call this thread manger
        user = kwargs.get("user")

        # Lookup criteria to find threads where the user is either the first or second person
        lookup = Q(user1=user) | Q(user2=user)

        # Get all unique threads matching the lookup criteria
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thread_user1",
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thread_user2",
    )
    updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()  # Custom manager for Thread model

    class Meta:
        unique_together = [
            "user1",
            "user2",
        ]  # Ensures only one thread for a pair of participants

    def __str__(self):
        return f"Thread {self.id} - {self.user1} and {self.user2}"


class ChatMessage(models.Model):
    thread = models.ForeignKey(
        Thread,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to=f"{settings.AWS_BASE_UPLOAD_PATH}/message_images",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} from {self.sender} in Thread {self.thread_id}"
