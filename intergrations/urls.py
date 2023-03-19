#from .views import CreateDeploymentView
from django.urls import path
from .views import GithubWebhook, DockerHubWebhook, GithubInstallationList

urlpatterns = [
    path("webhook/gh/", GithubWebhook.as_view(), name="Github Webhook"),
    path("webhook/dh/<project_uuid>/",
         DockerHubWebhook.as_view(), name="Docker Hub Webhook"),
    path("gh/installations/", GithubInstallationList.as_view(),
         name="Github Installation List"),
]
