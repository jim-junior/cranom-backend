import hashlib
import hmac
from rest_framework.request import Request
from users.models import UserProfile
from intergrations.models import GithubInstallation
from django.conf import settings
from deployments.models import Deployment, Project


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
    if UserProfile.objects.filter(github_id=sender["id"]).exists():
        user = UserProfile.objects.get(github_id=sender["id"])
        installation_obj = GithubInstallation.objects.create(
            github_id=data["installation"]["id"],
            account=user,
            account_type=data["installation"]["account"]["type"],
            gh_account_id=data["installation"]["account"]["id"],
        )
        installation_obj.save()


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
    if Project.objects.filter(git_repo=repository["full_name"], gh_update_on_push=True).exists():
        pass


def handle_release_published(data: dict):
    """
    Creates new deployments when a release is published for all projects with that repo
    """
    repository = data["repository"]
    if Project.objects.filter(git_repo=repository["full_name"], gh_update_on_release=True).exists():
        pass
