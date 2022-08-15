from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from .models import *
from .serializers import *
#from .utils.kube.dep import create_ingress, create_service, create_deployment


class CreateDeployment(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DeploymentSerializer
    queryset = Deployment.objects.all()

    def post(self, request):
        data = request.data
        serializer = DeploymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


class CreateDockerDeployment(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DockerDeploymentSerializer
    queryset = DockerDeployment.objects.all()

    def post(self, request):
        data = request.data
        serializer = DockerDeploymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            """ create_deployment(
                request.user.username,
                serializer.data['name'],
                serializer.data['image'],
                serializer.data['port'],
                # Environment variables
                serializer.data['env_variables'],
            ) """
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
