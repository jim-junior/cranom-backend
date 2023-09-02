from django.urls import path, re_path

from .consumers import NodeLogsConsumer, NodeDeploymentProgressConsumer

deployments_urlpatterns = [

    # A re_path for NodeLogsConsumer (which is async) that has route params and node_id of `int` type.
    re_path(
        r'^logs/node/(?P<node_id>\d+)/(?P<token>[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*)/$',
        NodeLogsConsumer.as_asgi()
    ),
    re_path(
        r'^logs/building/(?P<node_id>\d+)/(?P<token>[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*)/$',
        NodeDeploymentProgressConsumer.as_asgi()
    )

]
