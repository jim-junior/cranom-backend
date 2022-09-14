import json
import httpx
from kubernetes import client, config
# from ....kube.config import get_api_client_config


""" clientConfig = get_api_client_config()
k8s_client = client.ApiClient(clientConfig)

v1 = client.CoreV1Api(k8s_client) """
config.load_kube_config()

# A function that creates a new namespace in the cluster for a given User
v1 = client.CoreV1Api()


def create_namespace(user):
    namespace = client.V1Namespace(
        metadata=client.V1ObjectMeta(name=user.username),
        spec=client.V1NamespaceSpec(
            finalizers=["kubernetes"]
        )
    )
    try:
        resp = v1.create_namespace(namespace)
        print("Namespace created. status='%s'" % resp.status)
    except Exception as e:
        print("Exception when creating namespace: %s" % e)
        return False
    return True
