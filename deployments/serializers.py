from rest_framework import serializers
from .models import *


class DeploymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deployment
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
