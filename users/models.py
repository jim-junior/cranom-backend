from django.db import models
from django.contrib.auth.models import User

# Create your models here.


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


# A teams model. Each team has a name, a description, and a list of members. The members are represented as a list of usernames.
class Team(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField()
    members = models.ManyToManyField(UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
