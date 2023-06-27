#from .views import CreateDeploymentView
from django.urls import path
from .views.cli import (CreateDeployment, CreateProject, GetProjectInfo,)
from .views.base import (
    ProjectDetails,
    ProjectDeployments,
    ProjectList,
    StarProjectAPIView,
    GetWebSocketToken,
    CreateDeploymentFromUI,
    ProjectDeployments,
    CreateGitHubProject,
    ChangeProjectWebhookURL,
    ChangeProjectEnvVariables,
    ChangeProjectGitConfig,
    DeleteProject,
    CreateGitHubProjectNew,
)
from .views.project import ReDeployLatestDeployment, TurnNodeOffAndOn, UpdateEnvironmentVariables, DeleteNode, ListInstallationGHRepositories, CheckNodeName, ListUserAllGitHubInstallations, CreateProject

from .views.nodes import CreateNode

urlpatterns = [
    path("create/", CreateDeployment.as_view(), name="Create deployment"),
    path("project/deploy/", ReDeployLatestDeployment.as_view(),
         name="Re Deploy Project Project"),
    path("get/token/ws/", GetWebSocketToken.as_view(), name="Create deployment"),
    path("create/project/", CreateProject.as_view(), name="Create Project"),
    path("get/project/info/", GetProjectInfo.as_view(), name="Get Project Info"),
    path("get/projects/all/", ProjectList.as_view(), name="Get Projects "),
    path("project/star/", StarProjectAPIView.as_view(), name="STar project "),
    path("get/project/<uuid>/", ProjectDetails.as_view(), name="Project DEtails"),
    path("get/project/<project>/deployments/",
         ProjectDeployments.as_view(), name="Project Deployments"),
    path("create/github/project/", CreateGitHubProject.as_view(),
         name="Create GitHub Project"),
    path("project/change-webhook/", ChangeProjectWebhookURL.as_view(),
         name="Change project webhook URL"),
    path("project/change-envs/", ChangeProjectEnvVariables.as_view(),
         name="Change project Environment Variables"),
    path("project/change-git-config/", ChangeProjectGitConfig.as_view(),
         name="Change project Environment Variables"),
    path("project/delete/", DeleteProject.as_view(),
         name="Delete Project"),
    path("project/create/gh/new/", CreateGitHubProjectNew.as_view(),
         name="Create new GiTHUB Project"),
    path("node/switch/", TurnNodeOffAndOn.as_view(),
         name="Turn node on and off"),
    path("node/envs/update/", UpdateEnvironmentVariables.as_view(),
         name="Update node envs"),
    path("node/delete/", DeleteNode.as_view(),
         name="Delete Node"),
    path("get/installation/repositories/", ListInstallationGHRepositories.as_view(),
         name="List Installation Repositories"),
    path("check/node/name/", CheckNodeName.as_view(), name="Check Node Name"),
    path("get/installations/all/", ListUserAllGitHubInstallations.as_view(),
         name="List User All GitHub Installations"),
    path("create-node/<project_uuid>/", CreateNode.as_view(),
         name="Create Node for Project"),
    path("project/create/", CreateProject.as_view(), name="Create Project"),

]
