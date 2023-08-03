from django.contrib import admin
from events.models import Events


# Register your models here.
@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ["event_name", "event_content", "location", "created_at"]
