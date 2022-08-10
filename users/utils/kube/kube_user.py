import json
import httpx
from kubernetes import client, config

try:
    config.load_incluster_config()
    print("Loaded cluster config")
except config.config_exception.ConfigException:
    config.load_kube_config()


v1 = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()
networking_v1_api = client.NetworkingV1Api()

# A function that creates a new namespace in the cluster for a given User
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