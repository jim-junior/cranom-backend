from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from deployments.models import Project, Deployment, Node
from deployments.serializers import ProjectSerializer, ProjectNodeSerializer, DeploymentSerializer, NodeSerializer, DomainNameSerializer
from deployments.tasks.node import deploy_node


class CreateNode(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, project_uuid: int):
        # Check if the user is the owner of the project
        data = request.data
        nodename = data["name"]  # type: ignore

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

        serializer = NodeSerializer(data=data)  # type: ignore
        if serializer.is_valid():
            node = serializer.save(project=project)
            deploy_node(node.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetProjectNodes(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        data = request.data
        project_uuid = data["project_uuid"]  # type: ignore
        try:
            project = Project.objects.get(project_uuid=project_uuid)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        nodes = Node.objects.filter(project=project)
        project.nodes = nodes  # type: ignore
        serializer = ProjectNodeSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)
