import json
import httpx
from kubernetes import client, config
from kube.config import get_api_client_config
import yaml
from yaml.loader import BaseLoader


clientConfig = get_api_client_config()
k8s_client = client.ApiClient(clientConfig)

v1 = client.CoreV1Api(k8s_client)


# A function that creates a new namespace in the cluster for a given User
#v1 = client.CoreV1Api()


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
        create_docker_pull_secret(user)
    except Exception as e:
        print("Exception when creating namespace: %s" % e)
        return False
    return True


# A function that creates a kubernetes secret for the user
def create_docker_pull_secret(user):
    git_secret = f"""
apiVersion: v1
kind: Secret
metadata:
  name: docker-configjson
type: kubernetes.io/dockerconfigjson
stringData:
  .dockerconfigjson: |
    {
      "auths": {
        "https://index.docker.io/v1/": {
          "auth": "amltanVuaW9yYjpjaHJpc2Jyb3duYWxzaW5h"
        }
      }
    }
"""
    di = yaml.load(git_secret, BaseLoader)
    resp = v1.create_namespaced_secret(user.username, di)
