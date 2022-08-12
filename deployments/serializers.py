from rest_framework import serializers
from .models import *


class DeploymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deployment
        fields = "__all__"


class DockerDeploymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = DockerDeployment
        fields = "__all__"
