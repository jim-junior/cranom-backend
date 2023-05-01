from django.db import models
from users.models import UserProfile, Team

# Create your models here.


class GithubInstallation(models.Model):
    """
    A model that represents a Github installation
    """

    class Meta:
        verbose_name = "Github Installation"
        verbose_name_plural = "Github Installations"

    github_id = models.IntegerField()
    account = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="github_installations"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="github_installations", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_type = models.CharField(max_length=255, blank=True, null=True)
    gh_account_id = models.IntegerField()
    suspended = models.BooleanField(default=False)
    sender_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Github Installation {self.github_id}"

    def __repr__(self):
        return f"Github Installation {self.github_id}"

    def __unicode__(self):
        return f"Github Installation {self.github_id}"
