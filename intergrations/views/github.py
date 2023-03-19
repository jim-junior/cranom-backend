import hashlib
import hmac
from rest_framework.request import Request
from users.models import UserProfile
from intergrations.models import GithubInstallation
from django.conf import settings
from deployments.models import Deployment, Project, Node
from users.models import Notification
from deployments.utils.deployment import create_deployment_task
from rest_framework.renderers import JSONRenderer
from deployments.serializers import ProjectNodeSerializer


def verify_signature(request: Request):
    """
    Verifies the signature of the webhook requests from Github
    """
    signature = request.headers.get("X-Hub-Signature-256")
    if signature:
        digest = hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode(), request.body, hashlib.sha256
        ).hexdigest()
        if hmac.compare_digest(signature, "sha256=" + digest):
            return True
    else:
        return False


def gh_initialize(request: Request):
    """
    Handles all webhook requests from Github
    """
    # Get Headers
    event = request.headers.get("X-GitHub-Event")
    delivery = request.headers.get("X-GitHub-Delivery")
    # Get Payload
    data = request.data

    if event == "installation":
        if data["action"] == "created":
            install_app(data)
        elif data["action"] == "deleted":
            uninstall_app(data)
        elif data["action"] == "suspended":
            suspend_app(data)
        elif data["action"] == "unsuspended":
            unsuspend_app(data)
    elif event == "push":
        handle_push_event(data)
    elif event == "release":
        if data["action"] == "published":
            handle_release_published(data)


def install_app(data: dict):
    """
    Installs the app on the user's account
    """
    sender = data.get("sender")
    # Check if user with sender id exists
    if UserProfile.objects.filter(gh_id=sender["id"]).exists():
        user = UserProfile.objects.get(gh_id=sender["id"])
        installation_obj = GithubInstallation.objects.create(
            github_id=data["installation"]["id"],
            account=user,
            account_type=data["installation"]["account"]["type"],
            gh_account_id=data["installation"]["account"]["id"],
        )
        installation_obj.save()
        # CReate a notification
        Notification.objects.create(
            user=user,
            title=f"Github App Installed",
            message=f"Github App installed on your account",
            link=f"/settings/integrations",
            notification_type="success",
        )


def suspend_app(data: dict):
    """
    Suspends the app from the user's account
    """
    if GithubInstallation.objects.filter(github_id=data["installation"]["id"]).exists():
        installation_obj = GithubInstallation.objects.get(
            github_id=data["installation"]["id"]
        )
        installation_obj.suspended = True
        installation_obj.save()


def unsuspend_app(data: dict):
    """
    Unsuspends the app from the user's account
    """
    if GithubInstallation.objects.filter(github_id=data["installation"]["id"]).exists():
        installation_obj = GithubInstallation.objects.get(
            github_id=data["installation"]["id"]
        )
        installation_obj.suspended = False
        installation_obj.save()


def uninstall_app(data: dict):
    """
    Uninstalls the app from the user's account
    """
    if GithubInstallation.objects.filter(github_id=data["installation"]["id"]).exists():
        installation_obj = GithubInstallation.objects.get(
            github_id=data["installation"]["id"]
        )
        installation_obj.delete()


def handle_push_event(data: dict):
    """
    Creates new deployments when a push event is received for all projects with that repo
    """
    repository = data["repository"]
    # Get all Projects which have a node that has the same repo
    projects = Project.objects.filter(
        nodes__repository=repository["full_name"]
    ).distinct()

    # For each project in projects
    for project in projects:
        # Get all nodes with the same repo
        nodes = Node.objects.filter(
            repository=repository["full_name"], project=project)
        # For each node in nodes
        for node in nodes:
            node.git_revision = data["head_commit"]["id"]
            node.save()
            not_msg = f"""A new Deployment of node <b>{node.name}</b> in <b>{project.name}</b> was created through GitHub by <a href="https://github.com/{data["pusher"]["username"]}">{data["pusher"]["username"]}</a>"""
            Notification.objects.create(
                user=project.user,
                title=f"New deployment  created for {project.name}",
                message=not_msg,
                link=data["head_commit"]["url"],
                link_text="View commit on Github",
                notification_type="success",
            )
        # Create a new deployment
        project.nodes = project.node_set.all()
        serializer = ProjectNodeSerializer(project)
        deployment = Deployment.objects.create(
            project=project,
            version=project.deployment_set.count(),
            user=project.user,
            deployment_cfg=JSONRenderer().render(serializer.data).decode('utf-8'),
            nodes=JSONRenderer().render(
                serializer.data['nodes']).decode('utf-8')
        )

        # Run the deployment task
        create_deployment_task.delay(deployment.id)


def handle_release_published(data: dict):
    """
    Creates new deployments when a release is published for all projects with that repo
    """
    repository = data["repository"]
