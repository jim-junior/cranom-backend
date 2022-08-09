from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from .models import *
from .serializers import DeploymentSerializer


class CreateDeployment(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer = DeploymentSerializer

    def post(self, request):
        data = request.data
        return Response(data={}, status=status.HTTP_200_OK)
