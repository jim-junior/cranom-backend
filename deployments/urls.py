#from .views import CreateDeploymentView
from django.urls import path
from .views import CreateDeployment

urlpatterns = [
    path("create/", CreateDeployment.as_view(), name="Create deployment"),
]
