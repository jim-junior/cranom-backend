
from django.db import models
from django.contrib.auth.models import User
import uuid
from users.models import UserProfile
# Create your models here.


class Project(models.Model):
    readable_name = models.CharField(max_length=32, blank=True, null=True)
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
    favorite = models.BooleanField(default=False)
    project_cfg = models.JSONField(blank=True, null=True)
    webhook = models.URLField(blank=True, null=True)
    webhook_secret = models.CharField(max_length=100, blank=True, null=True)
    gh_update_on_push = models.BooleanField(
        default=False, blank=True, null=True)
    gh_update_on_pr_merge = models.BooleanField(
        default=False, blank=True, null=True)
    gh_update_on_release = models.BooleanField(
        default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.project_uuid}"


class Deployment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField()
    zipped_project = models.FileField(
        upload_to='delopyments/%Y/%m/%d/', blank=True)
    git_repo = models.CharField(max_length=200, blank=True, null=True)
    git_revision = models.CharField(max_length=200, blank=True, null=True)
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
    deployment_cfg = models.JSONField(blank=True, null=True)
    pipeline_cfg = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.deployment_uuid
