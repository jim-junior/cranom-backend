#from .views import CreateDeploymentView
from django.urls import path
from .views.cli import (CreateDeployment, CreateProject, GetProjectInfo,)
from .views.base import ProjectDetails, ProjectDeployments, ProjectList, StarProjectAPIView

urlpatterns = [
    path("create/", CreateDeployment.as_view(), name="Create deployment"),
    path("create/project/", CreateProject.as_view(), name="Create Project"),
    path("get/project/info/", GetProjectInfo.as_view(), name="Get Project Info"),
    path("get/projects/all/", ProjectList.as_view(), name="Get Projects "),
    path("project/star/", StarProjectAPIView.as_view(), name="STar project "),
    path("get/project/<uuid>/", ProjectDetails.as_view(), name="Project DEtails"),
    path("get/project/<project>/deployments/",
         ProjectDeployments.as_view(), name="Project DEtails")

]
