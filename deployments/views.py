from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from .serializers import DeplomentSerializer, Deployment
from rest_framework import generics
from utils.deployments import createDeployment, createService

""" 
class CreateDeploymentView(generics.CreateAPIView):
    serializer_class = DeplomentSerializer

    def create(self, request: Request, *args, **kwargs):
        data = request.data
        data.user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        name = serializer.data['name']
        image = serializer.data['image']
        replicas = serializer.data['replicas']
        user = request.user
        namespace = user.username
        port = serializer.data['port']
        createDeployment(name, image, replicas, port, namespace)
        createService(name, port, namespace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
 """