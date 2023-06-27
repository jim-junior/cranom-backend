from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from deployments.models import Project, Deployment, Node
from deployments.serializers import ProjectSerializer, ProjectNodeSerializer, DeploymentSerializer, NodeSerializer


# An APIView that creates a Node for a Project
class CreateNode(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, project_uuid: int):
        # Check if the user is the owner of the project
        try:
            project = Project.objects.get(project_uuid=project_uuid)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Create the Node
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
