#from .views import CreateDeploymentView
from django.urls import path
from .views import CreateDeployment, CreateDockerDeployment

urlpatterns = [
    path("create/git/", CreateDeployment.as_view(), name="Create deployment"),
    path("create/docker/", CreateDockerDeployment.as_view(),
         name="Create Docker deployment"),
]
