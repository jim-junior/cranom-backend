from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create your models here.

ACCOUNT_PLANS = (
    ("hobby", "hobby"),
    ("pro", "pro"),
    ("enterprise", "enterprise"),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    is_active = models.BooleanField(default=False)
    username = models.CharField(max_length=50)
    gh_id = models.CharField(max_length=12, blank=True)
    avatar = models.TextField(blank=True,)
    account_credit = models.IntegerField(default=0)
    country = models.CharField(max_length=20, default="uganda")
    created_at = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=4, default="USD")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    plan = models.CharField(
        max_length=10, choices=ACCOUNT_PLANS, default='hobby')
    active_channel_layer = models.CharField(
        max_length=100, default=None, null=True, blank=True)


# A teams model. Each team has a name, a description, and a list of members. The members are represented as a list of usernames.
class Team(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField()
    members = models.ManyToManyField(UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Notification(models.Model):

    class Meta:
        ordering = ['-created_at']

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.TextField()
    title = models.CharField(max_length=20, blank=True)
    link = models.CharField(max_length=100, blank=True, null=True)
    platform_notification = models.BooleanField(default=False)
    link_text = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    deployment_uuid = models.CharField(max_length=100, blank=True, null=True)
    project_uuid = models.CharField(max_length=100, blank=True, null=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, default="info")

    def __str__(self):
        return self.message


class AuthTokens(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    token = models.ForeignKey(
        Token, on_delete=models.CASCADE, related_name='token')
    created_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=100, blank=True)
    host = models.CharField(max_length=100, blank=True)
    platform = models.CharField(max_length=100, blank=True)
    ip = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.token
