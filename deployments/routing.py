from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'logs/(?P<uuid>\w+)/$', consumers.LogingConsumer.as_asgi()),
]
