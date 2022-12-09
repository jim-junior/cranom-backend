from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from .github import gh_initialize, verify_signature
from deployments.models import Deployment, Project
from users.models import UserProfile
import httpx
from deployments.views.cli import create_from_deployment
import datetime

# A classbased API view that handles all webhook requests from Github


class GithubWebhook(APIView):
    """
    An API endpoint that handles all webhook requests from Github
    """

    def post(self, request):
        """
        Handles all webhook requests from Github
        """
        # Verify the signature of the request
        if verify_signature(request):
            # Initialize the request
            gh_initialize(request)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

# A classbased API view that handles all webhook requests from Docker Hub.


class DockerHubWebhook(APIView):
    """
    An API endpoint that handles all webhook requests from Docker Hub
    """

    def post(self, request, project_uuid):
        """
        Handles all webhook requests from Docker Hub
        """
        data = request.data
        if Project.objects.filter(uuid=project_uuid).exists():
            project = Project.objects.get(uuid=project_uuid)
            if project.project_type == "docker":
                img_repo = data["repository"]["repo_name"]
                img_tag = data["push_data"]["tag"]
                docker_img = f"{img_repo}:{img_tag}"
                deployment = Deployment.objects.create(
                    user=project.user,
                    project=project,
                    image=docker_img,
                    version=project.deployment_set.count() + 1,
                    pipeline_cfg=data,
                )
                deployment.save()
                create_from_deployment(
                    project.user.username,
                    project.name,
                    docker_img,
                    project.port,
                    [],
                    project.deployed,
                )
                print(
                    f"Deployed project {project.project_uuid} with image {docker_img} through Docker Hub. ETA: {datetime.datetime.now()}")

                # Validate the webhook request
                callback_payload = {
                    "state": "success",
                    "description": f"Deployment v{project.deployment_set.count() + 1} created",
                    "context": "Cranom CI/CD Pipeline deployment - Docker Hub",
                }
                httpx.post(
                    data["callback_url"],
                    json=callback_payload,
                    headers={"Content-Type": "application/json"},
                )
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
