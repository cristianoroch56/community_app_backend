from django.urls import path
from help_and_support.views import HelpAndSupportAPIView

urlpatterns = [
    path("", HelpAndSupportAPIView.as_view(), name="help_and_support"),
]
