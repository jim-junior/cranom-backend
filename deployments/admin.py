from django.contrib import admin
from .models import Deployment, Project

# Register your models here.

admin.site.register(Deployment)
admin.site.register(Project)
