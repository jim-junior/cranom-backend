from deployments.models import Deployment, Project
from deployments.utils.kube_utils.kp_image import create_git_secret, create_kp_image, create_proj_sva, create_kp_builder
from celery import shared_task
from intergrations.models import GithubInstallation
from users.models import UserProfile
from intergrations.github.installation_access import get_installation_token


@shared_task
def create_gh_deployment(project_uuid, deployment_uuid):
    project: Project = Project.objects.get(project_uuid=project_uuid)
    deployment: Deployment = Deployment.objects.get(
        deployment_uuid=deployment_uuid)

    user: UserProfile = project.user

    gh_installation: GithubInstallation = GithubInstallation.objects.get(
        account=project.user)

    token = get_installation_token(gh_installation.github_id)
    create_git_secret(token, "x-access-token", project.name, user.username)
    # create service account
    create_proj_sva(project, user.username)
    # create builder
    create_kp_builder(project, deployment, user.username)
    # create image
    create_kp_image(project, deployment, user.username)
