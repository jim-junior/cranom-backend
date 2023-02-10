
from django.db import models
from django.contrib.auth.models import User
import uuid
from users.models import UserProfile
# Create your models here.


PROJECT_PLANS = (
    ("hobby", "hobby"),
    ("micro", "micro"),
    ("standard", "standard"),
    ("medium", "medium"),
    ("large", "large"),
    ("xlarge", "xlarge"),
    ("2xlarge", "2xlarge"),
)


class Project(models.Model):
    readable_name = models.CharField(max_length=32, blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_on = models.DateTimeField(blank=True, null=True)
    stopped_on = models.DateTimeField(blank=True, null=True)
    bill_accumulated = models.FloatField(blank=True, null=True)
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
        default=True, blank=True, null=True)
    gh_update_on_pr_merge = models.BooleanField(
        default=False, blank=True, null=True)
    gh_update_on_release = models.BooleanField(
        default=False, blank=True, null=True)
    last_charged = models.DateTimeField(
        blank=True, null=True, auto_now_add=True)
    plan = models.CharField(
        max_length=10, choices=PROJECT_PLANS, default='free'
    )

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


class DomainName(models.Model):
    domain_name = models.CharField(max_length=100)
    project = models.ForeignKey(
        Project,
        to_field="project_uuid",
        on_delete=models.CASCADE
    )
    third_party = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain_name
