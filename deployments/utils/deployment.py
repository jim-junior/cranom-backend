from typing import List
from deployments.models import Node, Project, Deployment
import json
from deployments.tasks.image import deploy_kp_image
from deployments.utils.kube_utils.git_deployment import create_git_node_deployment, create_git_node_service, create_node_ingress
from celery import shared_task
from intergrations.models import GithubInstallation
from users.models import UserProfile
from intergrations.github.installation_access import get_installation_token
from kubernetes import client, config, watch
from kube.config import get_api_client_config
from django.conf import settings
from deployments.utils.kube_utils.kp_image import (
    create_git_secret,
    create_kp_image,
    create_proj_sva,
    create_kp_builder,
)
from deployments.utils.kube_utils.git_deployment import (
    delete_git_node_deployment,
    delete_git_node_service,
    delete_git_node_ingress,
)
apiConfig = get_api_client_config()
apiclient = client.ApiClient(apiConfig)
v1 = client.CoreV1Api(apiclient)
apps_v1_api = client.AppsV1Api(apiclient)
networking_v1_api = client.NetworkingV1Api(apiclient)

crd_api = client.CustomObjectsApi(apiConfig)


def create_deployment(deployment: Deployment, prev_deploy: Deployment = None):

    if deployment.nodes is not None:
        nodes: List[Node] = json.loads(deployment.nodes)
        if prev_deploy is not None:
            prev_nodes: List[Node] = json.loads(prev_deploy.nodes)
            for node in prev_nodes:
                if node not in nodes:
                    if node.node_type == "git":
                        delete_git_node(node)
        if len(nodes) != 0:
            for node in nodes:
                if node.node_type == "git":
                    if node.running:
                        deploy_git_node(node)


def deploy_git_node(node: Node):
    project: Project = node.project
    user: UserProfile = project.user
    git_username = ""
    git_password = ""
    if node.custom_git_repo == False and node.is_public_repo == False:
        # If the node repo is a Github Repository
        gh_installation: GithubInstallation = GithubInstallation.objects.get(
            account=project.user)
        # Get GitHub App access token
        token = get_installation_token(gh_installation.github_id)
        git_username = "x-access-token"
        git_password = token
    elif node.custom_git_repo == True:
        git_username = node.git_repo_username
        git_password = node.git_repo_pswd

    if node.is_public_repo == True:
        create_proj_sva(node, user.username)
        # create image
        create_kp_image(project, node, user.username)
    else:
        create_git_secret(git_password, git_username, node.id, user.username)
        # create service account
        create_proj_sva(node, user.username)
        # create image
        create_kp_image(project, node, user.username)

    deploy_kp_image.delay(node.id)


def delete_git_node(node: Node):
    delete_git_node_deployment(node)
    delete_git_node_service(node)
    delete_git_node_ingress(node)


@shared_task
def create_deployment_task(deployment_uuid: str):
    deployment: Deployment = Deployment.objects.get(uuid=deployment_uuid)
    # Get previous deployment with second last created at date
    prev_deploy: Deployment = Deployment.objects.filter(
        project=deployment.project).order_by("-created_at")[1]
    create_deployment(deployment, prev_deploy=prev_deploy)
