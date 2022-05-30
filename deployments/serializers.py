from .models import Deployment
from rest_framework import serializers


class DeplomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deployment
        fields = "__all__"
