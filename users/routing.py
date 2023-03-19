from django.urls import path, re_path

from .consumers.user_session import UserSession

websocket_urlpatterns = [

    re_path(
        r'^session/(?P<token>[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*)/$',
        UserSession.as_asgi()
    )

]
