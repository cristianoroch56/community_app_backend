from django.contrib import admin
from pages.models import Pages


# Register your models here.
@admin.register(Pages)
class PagesAdmin(admin.ModelAdmin):
    list_display = ["slug", "body"]
