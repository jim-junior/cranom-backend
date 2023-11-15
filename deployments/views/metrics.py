from django.http import QueryDict
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from deployments.models import Node
from kube.metrics.memory import get_node_memory_usage


class GetNodeMemoryUsage(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        data: QueryDict = request.data  # type: ignore
        nodeid = data.get('nodeid')
        hours: int = data.get('hours')  # type: ignore
        if nodeid is None or hours is None:
            print(nodeid, hours)
            return Response(
                data={
                    'error': 'nodeid and hours are required'
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        if Node.objects.filter(pk=nodeid).exists():
            node = Node.objects.get(pk=nodeid)
            memory_usage = get_node_memory_usage(node, hours)
            if memory_usage is None:
                return Response(
                    data={
                        'error': 'failed to get memory usage'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(
                data=memory_usage,
                status=status.HTTP_200_OK
            )
