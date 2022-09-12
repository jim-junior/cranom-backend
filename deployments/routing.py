from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('logs/', consumers.ChatConsumer.as_asgi()),
]
