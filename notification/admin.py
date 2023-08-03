from django.contrib import admin
from notification.models import SendNotification


# Register your models here.
@admin.register(SendNotification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "content", "is_read", "created_at"]
