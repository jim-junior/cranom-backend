from django.http import QueryDict
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import permissions
from intergrations.github.installation_access import get_installation_token
from intergrations.models import GithubInstallation
from ..models import *
from ..serializers import *
from rest_framework.renderers import JSONRenderer
from .cli import getUserProfile
import httpx
import datetime
from billing.tasks.projects import get_project_amount


class CreateProject(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        data: QueryDict = request.data  # type: ignore
        data['user'] = request.user.id
        serializer = ProjectSerializer(data=data)  # type: ignore
        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            data=serializer.errors,
            status=status.HTTP_406_NOT_ACCEPTABLE
        )


class ReDeployLatestDeployment(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        data = request.data
        project_uuid = data['project']  # type: ignore
        if Project.objects.filter(project_uuid=project_uuid).exists():
            project = Project.objects.get(project_uuid=project_uuid)
            project.nodes = project.node_set.all()  # type: ignore
            serializer = ProjectNodeSerializer(project)
            deployment = Deployment.objects.create(
                project=project,
                version=project.deployment_set.count(),  # type: ignore
                user=project.user,
                deployment_cfg=JSONRenderer().render(serializer.data).decode('utf-8'),
                nodes=JSONRenderer().render(
                    serializer.data['nodes']).decode('utf-8')
            )

            project.deployed = True
            project.save()
            # create_deployment_task.delay(deployment.uuid)
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
        nodeid = request.data.get('node')  # type: ignore
        running: bool | None = request.data.get('running')  # type: ignore
        if running is None:
            return Response(data={
                'message': 'Invalid Data'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        if Node.objects.filter(pk=nodeid).exists():
            node = Node.objects.get(pk=nodeid)
            node.running = running
            if running == False:
                # Calculate the amount of time the node has been running
                # Get the last time the node was turned on
                last_turned_on = node.started_on

                if last_turned_on is None:
                    last_turned_on = datetime.datetime.now()
                # Get the current time
                now = datetime.datetime.now()
                # Get the difference between the two
                diff = now - last_turned_on
                amount = get_project_amount(node.plan, diff.total_seconds())
                if node.bill_accumulated is None:
                    node.bill_accumulated = amount
                else:
                    node.bill_accumulated += amount
                node.stopped_on = now
            else:
                node.started_on = datetime.datetime.now()

            node.save()
            return Response(status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Node does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class UpdateEnvironmentVariables(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = getUserProfile(request.user)
        nodeid = request.data.get('node')  # type: ignore
        envs = request.data.get('env_vars')  # type: ignore
        if Node.objects.filter(pk=nodeid).exists():
            node = Node.objects.get(pk=nodeid)
            project = node.project
            node.env_variables = envs  # type: ignore
            node.save()
            return Response(status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Node does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class DeleteNode(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = getUserProfile(request.user)
        nodeid = request.data.get('node')  # type: ignore
        if Node.objects.filter(pk=nodeid).exists():
            node = Node.objects.get(pk=nodeid)
            node.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Node does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


# An Api View that checks if there is a node inthe project with the same name as the posted string


class CheckNodeName(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        project_uuid = request.data.get('project_uuid')  # type: ignore
        node_name = request.data.get('node_name')  # type: ignore
        if node_name == "":
            return Response(data={
                'message': 'Node Name Already Exists'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        if Project.objects.filter(project_uuid=project_uuid).exists():
            project = Project.objects.get(project_uuid=project_uuid)
            if Node.objects.filter(project=project, name=node_name).exists():
                return Response(data={
                    'message': 'Node Name Already Exists'
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            return Response(status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Project Does Not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class GithubInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubInstallation
        fields = '__all__'


class ListUserAllGitHubInstallations(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        user = getUserProfile(request.user)
        if GithubInstallation.objects.filter(account=user).exists():
            installations = GithubInstallation.objects.filter(account=user)
            serializer = GithubInstallationSerializer(installations, many=True)
            return Response(data={
                'installations': serializer.data,
                "exists": True
            }, status=status.HTTP_200_OK)
        return Response(data={
            'message': 'No Github Installation Found',
            "exists": False
        }, status=status.HTTP_204_NO_CONTENT)


class ListInstallationGHRepositories(APIView):

    def get_repositories(self, installationId):
        installation_token = get_installation_token(installationId)
        resp = httpx.get(
            f"https://api.github.com/installation/repositories", headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {installation_token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }, timeout=None
        )
        return resp.json()

    def post(self, request: Request):
        installationId = request.data.get('installationId')  # type: ignore
        if installationId:
            repositories = self.get_repositories(installationId)
            return Response(data=repositories["repositories"], status=status.HTTP_200_OK)
        return Response(data={
            'message': 'No Github Installation Found'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)
