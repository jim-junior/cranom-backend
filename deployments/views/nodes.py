from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from deployments.models import Project, Deployment, Node
from deployments.serializers import ProjectSerializer, ProjectNodeSerializer, DeploymentSerializer, NodeSerializer
from deployments.tasks.node import deploy_node

# An APIView that creates a Node for a Project


class CreateNode(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, project_uuid: int):
        # Check if the user is the owner of the project
        data = request.data
        nodename = data["name"]

        # Check if the node name is already in use
        if Node.objects.filter(name=nodename).exists():
            return Response(
                {"error": "A node with that name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(project_uuid=project_uuid)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = NodeSerializer(data=data)
        if serializer.is_valid():
            node = serializer.save(project=project)
            print(node.id)
            deploy_node(node.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
