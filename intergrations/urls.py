#from .views import CreateDeploymentView
from django.urls import path
from .views import CreateDeployment

urlpatterns = [
    path("webhook/git/", CreateDeployment.as_view(), name="Create deployment"),
]
