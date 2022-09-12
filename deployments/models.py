
from django.db import models
from django.contrib.auth.models import User
import uuid
from users.models import UserProfile
# Create your models here.


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    port = models.IntegerField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
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
    project_type = models.CharField(max_length=10, blank=False)
    run_command = models.CharField(max_length=100, blank=True, null=True)
    build_command = models.CharField(max_length=100, blank=True, null=True)
    env_variables = models.JSONField(blank=True, null=True)
    deployed = models.BooleanField(default=False)


class Deployment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()
    zipped_project = models.FileField(
        upload_to='delopyments/%Y/%m/%d/', blank=True)
    git_repo = models.CharField(max_length=200, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    deployment_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    project = models.ForeignKey(
        Project,
        to_field="project_uuid",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
