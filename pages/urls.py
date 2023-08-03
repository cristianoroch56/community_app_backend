from django.urls import path
from pages.views import PagesAPIView

urlpatterns = [
    path("", PagesAPIView.as_view(), name="get_pages")
]
