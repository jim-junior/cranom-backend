from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from ..models import *
from ..serializers import *
from ..utils.kube_utils.dep import create_ingress, create_service, create_deployment


def getUserProfile(user):
    profile = UserProfile.objects.get(user=user)
    return profile


def create_from_deployment(username, name, image, port, envs, deployed):
    create_deployment(username, name, image, port, envs, deployed)
    create_service(name, port, username, deployed)
    create_ingress(name, port, username, deployed)


class CreateDeployment(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DeploymentSerializer
    queryset = Deployment.objects.all()

    def post(self, request):
        data = request.data
        serializer = DeploymentSerializer(data=data)
        if serializer.is_valid():
            dep = serializer.save()
            proj = dep.project
            deployed = proj.deployed
            if proj.deployed == False:
                proj.deployed = True
                proj.save()
            if proj.project_type == "docker":
                #
                userprofile = getUserProfile(request.user)
                username = userprofile.username
                create_from_deployment(
                    username, proj.name, dep.image, proj.port, [], deployed)
                pass
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


class GetProjectInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = request.data
        user = request.user
        prof = getUserProfile(user)
        proj_name = data["project"]
        project_set = Project.objects.filter(user=prof)
        if project_set.filter(name=proj_name).exists():
            proj = Project.objects.get(name=proj_name)
            ver = proj.deployment_set.count()
            puuid = proj.project_uuid
            typ = proj.project_type
            data["version"] = ver
            return Response(data={
                "exists": True,
                "name": proj_name,
                "version": ver,
                "uuid": puuid,
                "deployed": False,
                "type": typ
            }, status=status.HTTP_200_OK)
        return Response(data={
            "message": "Project Does not exist"
        }, status=status.HTTP_404_NOT_FOUND)

# "0777118276"


class CreateProject(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer
    queryset = Deployment.objects.all()

    def post(self, request):
        data = request.data
        user = request.user
        projname = data["name"]
        prof = getUserProfile(user)
        project_set = Project.objects.filter(user=prof)
        if project_set.filter(name=projname).exists():
            return Response(data={"name": ["Project with this name already exists"]}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
