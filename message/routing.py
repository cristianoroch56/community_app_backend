from django.urls import path
from message.consumer import ChatConsumer


websocket_urlpatterns = [
    path("ws/chat/<int:thread_id>/", ChatConsumer.as_asgi()),
]
