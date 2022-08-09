from rest_framework import serializers
from .models import *

class DeploymentSerializer(serializers.ModelSerializer):
	
	class Meta:
		fields = "__all__"