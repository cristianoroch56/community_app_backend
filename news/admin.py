from django.contrib import admin
from news.models import News


# Register your models here.
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["news_content", "news_title", "image", "created_at"]
