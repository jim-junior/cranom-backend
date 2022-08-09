from django.contrib import admin
from .models import Deployment, DeploymentEnvs

# Register your models here.

admin.site.register(Deployment)
admin.site.register(DeploymentEnvs)