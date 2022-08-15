
import time

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

# Authenticate to the kubernetes cluster
config.load_kube_config()

# Create a configuration object
configuration = Configuration()

# Set the default namespace
configuration.namespace = 'default'

# Create an API client object
api_client = core_v1_api.ApiClient(configuration)

# Create an API object
api = core_v1_api.CoreV1Api(api_client)

# A function that executes a command in a pod


def exec_command(pod_name, command):
    try:
        exec_command_response = api.connect_get_namespaced_pod_exec(
            pod_name,
            'default',
            command=command,
            stderr=True,
            stdin=True,
            stdout=True,
            tty=True
        )
        return exec_command_response
    except ApiException as e:
        print("Exception when calling CoreV1Api->connect_get_namespaced_pod_exec: %s\n" % e)
        return None

# A function that gets active pod in a deployment


def get_active_pod(deployment_name):
    try:
        deployment = api.read_namespaced_deployment(deployment_name, 'default')
        return deployment.status.ready_replicas
    except ApiException as e:
        print("Exception when calling CoreV1Api->read_namespaced_deployment: %s\n" % e)
        return None
