
from django.db import models
from django.contrib.auth.models import User
import uuid
from users.models import UserProfile
# Create your models here.


class Deployment(models.Model):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    port = models.IntegerField()
    git_repo = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    project_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    run_command = models.CharField(max_length=100, blank=True)
    build_command = models.CharField(max_length=100, blank=True)
    env_variables = models.JSONField(blank=True, null=True)
    deployed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DockerDeployment(models.Model):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    port = models.IntegerField()
    image = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    project_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    env_variables = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
