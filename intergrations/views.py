from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
#from .utils.kube.dep import create_ingress, create_service, create_deployment


class CreateDeployment(APIView):
    def post(self, request):
        data = request.data
        print(data)
        return Response(status=status.HTTP_201_CREATED)
