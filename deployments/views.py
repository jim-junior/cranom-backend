from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from .models import *
from .serializers import DeploymentSerializer


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
