from typing import List
from deployments.models import Node, Project, Deployment
from celery import shared_task

from deployments.utils.deployment import create_deployment


@shared_task
def create_deployment_task(deployment_uuid: str):
    deployment: Deployment = Deployment.objects.get(
        deployment_uuid=deployment_uuid)
    # Get previous deployment with second last created at date
    prev_deploy: Deployment = Deployment.objects.filter(
        project=deployment.project).order_by("-created_at")[1]
    create_deployment(deployment, prev_deploy=prev_deploy)
