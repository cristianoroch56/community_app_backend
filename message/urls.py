from django.urls import path
from message.views import ThreadsAPIView, MessagesAPIView

urlpatterns = [
    path("threads/", ThreadsAPIView.as_view(), name="threads"),
    path("messages/", MessagesAPIView.as_view(), name="messages"),
]
