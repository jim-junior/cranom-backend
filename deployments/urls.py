#from .views import CreateDeploymentView
from django.urls import path
from .views.cli import (CreateDeployment, CreateProject, GetProjectInfo,)

urlpatterns = [
    path("create/", CreateDeployment.as_view(), name="Create deployment"),
    path("create/project/", CreateProject.as_view(), name="Create Project"),
    path("get/project/info/", GetProjectInfo.as_view(), name="Get Project Info")

]
