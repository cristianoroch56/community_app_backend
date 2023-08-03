from django.urls import path
from notification.views import UserNotificationAPIView

urlpatterns = [
    path("", UserNotificationAPIView.as_view(), name="get_notification"),
    path("<int:pk>/", UserNotificationAPIView.as_view(), name="update_notification"),
    path("<int:pk>/", UserNotificationAPIView.as_view(), name="delete_notification"),
]
