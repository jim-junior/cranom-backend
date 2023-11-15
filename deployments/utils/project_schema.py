from deployments.serializers import NodeSerializer, ProjectSerializer
from rest_framework import serializers
from users.models import UserProfile
from deployments.models import Project, Deployment, Node
import yaml
from yaml.loader import BaseLoader
import json
from deployments.models import PROJECT_PLANS, PROCESS_TYPES, NODE_TYPES


class NodeSchema(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
    node_type = serializers.ChoiceField(choices=NODE_TYPES)
    size = serializers.ChoiceField(choices=PROJECT_PLANS, allow_blank=True)
    build_commands = serializers.CharField(
        max_length=None, min_length=None, allow_blank=True, required=False, trim_whitespace=False)
    run_command = serializers.CharField(
        max_length=None, min_length=None, required=False, allow_blank=True, trim_whitespace=False)


class CCSchema(serializers.Serializer):
    """ 
    Class that defines and validates cranom configuration file schema.
    """
    name = serializers.CharField(max_length=100, required=True)
    project_type = serializers.ChoiceField(choices=PROCESS_TYPES)
    nodes = NodeSchema(many=True, read_only=False, required=False)

    # Zip project file. This is not part of the Schema but is just needed incase the project is of type `local`
    zipped_project = serializers.FileField(required=False)


class CConfig():
    """ 
    Class that defines and validates cranom configuration file schema. Supports both `JSON` and `yaml`
    """
    errors = {}

    def __init__(self, data: str, user: UserProfile, _format=None) -> None:
        if _format == 'yaml':
            try:
                di = yaml.load(data, BaseLoader)
                self.data = di
            except:
                self.valid_format = False
                self.errors = {
                    'format': ['YAML is invalid']
                }
        elif _format == 'json':
            try:
                di = json.loads(data)
                self.data = data
            except:
                self.valid_format = False
                self.errors = {
                    'format': ['JSON is invalid']
                }
        elif _format == None:
            self.data = data
        else:
            self.valid_format = False
            self.errors = {
                'format': ['Format must be JSON or YAML']
            }
        self.user = user

    def is_valid(self) -> bool:
        """ Check if data Provided is Valid """
        if self.valid_format:
            serializer = CCSchema(data=self.data)
            if serializer.is_valid():
                return True
            else:
                self.errors = serializer.errors
                return False
        else:
            return False
