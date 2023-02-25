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


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = "__all__"


class ProjectNodeSerializer(serializers.ModelSerializer):
    nodes = NodeSerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = "__all__"
        extra_fields = ['nodes']

    def create(self, validated_data):
        nodes_data = validated_data.pop('nodes')
        project = Project.objects.create(**validated_data)
        for node_data in nodes_data:
            Node.objects.create(project=project, **node_data)
        return project
