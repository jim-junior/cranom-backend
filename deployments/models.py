
from django.db import models

# Create your models here.


class Deployment(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    app_label = models.CharField(max_length=100)
    api_version = models.CharField(max_length=100)
    kind = models.CharField(max_length=100)
    metadata = models.TextField()
    spec = models.TextField()
    status = models.TextField()

    def __str__(self):
        return self.name


class Pod(models.Model):
    deployment = models.ForeignKey(Deployment, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=100)
    image_pull_policy = models.CharField(max_length=100)
    container_port = models.IntegerField()
    container_name = models.CharField(max_length=100)


class PodEnvs(models.Model):
    pod = models.ForeignKey(Pod, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    value_from = models.TextField()
