#from .views import CreateDeploymentView
from django.urls import path
from .views import GithubWebhook, DockerHubWebhook, GithubInstallationList
from .views.platform import CheckGithubInstallation

urlpatterns = [
    path("webhook/gh/", GithubWebhook.as_view(), name="Github Webhook"),
    path("webhook/dh/<project_uuid>/",
         DockerHubWebhook.as_view(), name="Docker Hub Webhook"),
    path("gh/installations/", GithubInstallationList.as_view(),
         name="Github Installation List"),
    path("gh/check/", CheckGithubInstallation.as_view(),
         name="Check Github Installation"),
]
