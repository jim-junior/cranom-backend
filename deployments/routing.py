from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'^logs/(?P<uuid>[A-Za-z0-9_-]+)/(?P<token>[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*)/$',
            consumers.LogingConsumer.as_asgi()),
]
