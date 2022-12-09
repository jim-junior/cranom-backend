from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions

from deployments.utils.ws_token import encrypt
from ..models import *
from ..serializers import *
from .cli import create_from_deployment, getUserProfile


class ProjectDetails(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get(self, request, uuid):
        if Project.objects.filter(project_uuid=uuid).exists():
            obj = Project.objects.get(project_uuid=uuid)
            serialized = ProjectSerializer(obj)
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
