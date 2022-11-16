from deployments.models import Deployment, Project
from deployments.utils.kube_utils.kp_image import create_git_secret, create_kp_image
from celery import shared_task


@shared_task
def create_gh_deployment(project_uuid, deployment_uuid):
    project: Project = Project.objects.get(project_uuid=project_uuid)
    deployment: Deployment = Deployment.objects.get(
        deployment_uuid=deployment_uuid)
    pass
