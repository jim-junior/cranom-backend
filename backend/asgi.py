"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""


#import deployments.routing
from deployments.routing import websocket_urlpatterns
import deployments
from .channelsmiddleware import TokenAuthMiddleware
import os
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')


# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        # TokenAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
        # )
    ),
})
