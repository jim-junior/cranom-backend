from django.db import models

# Create your models here.


class Deployment(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)
    image = models.TextField()
    port = models.IntegerField(default=3000)
    replicas = models.IntegerField(default=1, null=True)
