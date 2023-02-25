from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from users.models import Notification
from deployments.utils.ws_token import encrypt
from ..models import *
from ..serializers import *
from rest_framework.renderers import JSONRenderer
from .cli import create_from_deployment, getUserProfile


class ReDeployLatestDeployment(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        data = request.data
        project_uuid = data['project']
        if Project.objects.filter(project_uuid=project_uuid).exists():
            project = Project.objects.get(project_uuid=project_uuid)
            project.nodes = project.node_set.all()
            serializer = ProjectNodeSerializer(project)
            deployment = Deployment.objects.create(
                project=project,
                version=project.deployment_set.count(),
                user=project.user,
                deployment_cfg=JSONRenderer().render(serializer.data).decode('utf-8'),
                nodes=JSONRenderer().render(
                    serializer.data['nodes']).decode('utf-8')
            )

            project.deployed = True
            project.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            data={
                'message': 'Project Does Not Exist'
            },
            status=status.HTTP_406_NOT_ACCEPTABLE
        )


class TurnNodeOffAndOn(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = getUserProfile(request.user)
        nodeid = request.data.get('node')
        running = request.data.get('running')
        if Node.objects.filter(pk=nodeid).exists():
            node = Node.objects.get(pk=nodeid)
            project = node.project
            node.running = running
            node.save()
            return Response(status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Node does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class UpdateEnvironmentVariables(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = getUserProfile(request.user)
        nodeid = request.data.get('node')
        envs = request.data.get('env_vars')
        if Node.objects.filter(pk=nodeid).exists():
            node = Node.objects.get(pk=nodeid)
            project = node.project
            node.env_variables = envs
            node.save()
            return Response(status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Node does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class DeleteNode(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = getUserProfile(request.user)
        nodeid = request.data.get('node')
        if Node.objects.filter(pk=nodeid).exists():
            node = Node.objects.get(pk=nodeid)
            node.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Node does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)
