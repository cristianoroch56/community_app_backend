from django.urls import path
from userprofile.views import UserProfileAPIView

urlpatterns = [
    path("", UserProfileAPIView.as_view(), name="user_profile"),
]
