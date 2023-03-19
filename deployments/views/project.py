from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from intergrations.github.installation_access import get_installation_token
from intergrations.models import GithubInstallation
from users.models import Notification
from deployments.utils.ws_token import encrypt
from ..models import *
from ..serializers import *
from rest_framework.renderers import JSONRenderer
from .cli import create_from_deployment, getUserProfile
import httpx


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


class ListInstallationGHRepositories(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_repositories(self, user: UserProfile):
        installation: GithubInstallation = GithubInstallation.objects.get(
            account=user
        )
        installation_token = get_installation_token(
            installation.github_id)
        resp = httpx.get(
            f"https://api.github.com/installation/repositories", headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {installation_token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }, timeout=None
        )
        return resp.json()

    def get(self, request: Request):
        user = getUserProfile(request.user)
        if GithubInstallation.objects.filter(account=user).exists():
            repositories = self.get_repositories(user)
            return Response(data=repositories["repositories"], status=status.HTTP_200_OK)
        return Response(data={
            'message': 'No Github Installation Found'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)
