from django.db import models


# Create your models here.
class Pages(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    body = models.TextField()

    class Meta:
        verbose_name = "Pages"
        verbose_name_plural = "Pages"
