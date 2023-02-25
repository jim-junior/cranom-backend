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
from .cli import create_from_deployment, getUserProfile


class ProjectDetails(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectNodeSerializer

    def get(self, request, uuid):
        if Project.objects.filter(project_uuid=uuid).exists():
            obj = Project.objects.get(project_uuid=uuid)
            obj.nodes = obj.node_set.all()
            serialized = ProjectNodeSerializer(obj)
            return Response(data=serialized.data, status=status.HTTP_200_OK)
        return Response(data={"message": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)


class ProjectDeployments(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DeploymentSerializer
    model = serializer_class.Meta.model
    paginate_by = 10

    def get_queryset(self):
        project_uuid = self.kwargs['project']
        queryset = self.model.objects.filter(project=project_uuid)
        return queryset.order_by('-created_at')


class ProjectList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer
    model = serializer_class.Meta.model
    paginate_by = 10

    def get_queryset(self):
        user = getUserProfile(self.request.user)
        queryset = self.model.objects.filter(user=user)
        return queryset.order_by("-favorite", '-created_at')


class StarProjectAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        p_uuid = data["uuid"]
        if Project.objects.filter(project_uuid=p_uuid).exists():
            obj = Project.objects.get(project_uuid=p_uuid)
            if obj.favorite == True:
                obj.favorite = False
            else:
                obj.favorite = True
            obj.save()
            return Response(data={"message": "Starred"}, status=status.HTTP_200_OK)
        return Response(data={"message": "Project does not exist"}, status=status.HTTP_404_NOT_FOUND)


class GetWebSocketToken(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        token = encrypt(user.username, user.id)
        return Response(data={"token": token}, status=status.HTTP_200_OK)


class CreateDeploymentFromUI(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        project_uuid = data["uuid"]
        if Project.objects.filter(project_uuid=project_uuid).exists():
            project = Project.objects.get(project_uuid=project_uuid)

            if project.project_type == "docker":
                deployment = Deployment.objects.create(
                    project=project,
                    image=project.image,
                    user=project.user,
                    version=project.deployment_set.count()
                )
                deployed = project.deployed
                project.deployed = True
                project.save()
                deployment.save()
                create_from_deployment(
                    project.user.username, project.name, project.image, project.port, [], deployed)
                return Response(status=status.HTTP_100_CONTINUE)
            elif project.project_type == "git":
                deployment = Deployment.objects.create(
                    project=project,
                    image=project.image,
                    user=project.user,
                    version=project.deployment_set.count()
                )
                deployed = project.deployed
                project.deployed = True
                project.save()
                deployment.save()
                return Response(status=status.HTTP_100_CONTINUE)
        return Response(data={"message": "Does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)


# A ListAPIView that shows the deployments of a project given the project uuid as a parameter and paginates the results in groups of 10
class ProjectDeployments(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DeploymentSerializer
    model = serializer_class.Meta.model
    paginate_by = 10

    def get_queryset(self):
        project_uuid = self.kwargs['project']
        queryset = self.model.objects.filter(project=project_uuid)
        return queryset.order_by('-created_at')


class CreateGitHubProject(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer

    def post(self, request):
        user = UserProfile.objects.get(user=request.user)
        data = request.data
        projname = data["name"]
        prof = getUserProfile(user)
        project_set = Project.objects.filter(user=prof)
        if project_set.filter(name=projname).exists():
            return Response(data={"message": "Project with this name already exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            project = serializer.save()
            # Create a notification for the user
            Notification.objects.create(
                user=user,
                message=f"Project <b>{projname}</b> created successfully.",
                project_uuid=project.project_uuid,
                link=f'/projects/p/{project.project_uuid}',
                link_text='View Project',
                title='New Project Created'
            )
            if data['autodeploy']:
                pass
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


class ChangeProjectWebhookURL(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        data = request.data
        project_uuid = data['project']
        webhook = data['webhook']
        if Project.objects.filter(project_uuid=project_uuid).exists():
            project = Project.objects.get(project_uuid=project_uuid)
            project.webhook = webhook
            project.save()
            return Response(data={
                'message': 'Project webhook URL successfully Changed'
            }, status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Project does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class ChangeProjectEnvVariables(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        data = request.data
        project_uuid = data['project']
        envs = data['env_variables']
        if Project.objects.filter(project_uuid=project_uuid).exists():
            project = Project.objects.get(project_uuid=project_uuid)
            project.env_variables = envs
            project.save()
            return Response(data={
                'message': 'Project Environment Variables successfully Changed'
            }, status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Project does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class ChangeProjectGitConfig(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        data = request.data
        project_uuid = data['project']
        gh_update_on_push = data['gh_update_on_push']
        gh_update_on_pr_merge = data['gh_update_on_pr_merge']
        gh_update_on_release = data['gh_update_on_release']
        if Project.objects.filter(project_uuid=project_uuid).exists():
            project = Project.objects.get(project_uuid=project_uuid)
            project.gh_update_on_release = gh_update_on_release
            project.gh_update_on_pr_merge = gh_update_on_pr_merge
            project.gh_update_on_push = gh_update_on_push
            project.save()
            return Response(data={
                'message': 'Project Github Config successfully Changed'
            }, status=status.HTTP_200_OK)
        return Response(data={
            'message': 'Project does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class DeleteProject(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        data = request.data
        user = getUserProfile(request.user)
        project_uuid = data['project']

        if Project.objects.filter(project_uuid=project_uuid).exists():
            project = Project.objects.get(project_uuid=project_uuid)
            if project.user == user:
                project.delete()
                return Response(data={
                    'message': 'Project successfully Deleted'
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    'message': 'Permission Denied'
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(data={
            'message': 'Project does not Exist'
        }, status=status.HTTP_406_NOT_ACCEPTABLE)


class CreateGitHubProjectNew(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectNodeSerializer

    def post(self, request):
        user = UserProfile.objects.get(user=request.user)
        data = request.data
        projname = data["name"]
        prof = getUserProfile(user)
        project_set = Project.objects.filter(user=prof)
        if project_set.filter(name=projname).exists():
            return Response(data={"message": "Project with this name already exists"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            project = serializer.save()
            # Create a notification for the user
            Notification.objects.create(
                user=user,
                message=f"Project <b>{projname}</b> created successfully.",
                project_uuid=project.project_uuid,
                link=f'/projects/p/{project.project_uuid}',
                link_text='View Project',
                title='New Project Created'
            )
            if data['autodeploy']:
                pass
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
