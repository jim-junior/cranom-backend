from deployments.routing import deployments_urlpatterns
from users.routing import websocket_urlpatterns

ws_routes = list()

ws_routes += deployments_urlpatterns
ws_routes += websocket_urlpatterns
