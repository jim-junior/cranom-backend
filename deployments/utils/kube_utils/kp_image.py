import json
import httpx
from kubernetes import client, config
from kube.config import get_api_client_config
import yaml
from yaml.loader import BaseLoader
from ...models import Deployment, Project, Node
from django.conf import settings

""" apiConfig = get_api_client_config()
apiclient = client.ApiClient(apiConfig)

custom_obj_api = client.CustomObjectsApi(apiclient)
core_api = client.CoreV1Api(apiclient) """
config.load_kube_config()
custom_obj_api = client.CustomObjectsApi()
core_api = client.CoreV1Api()

def create_kp_image(project: Project, node: Node, username: str):

    img_obj = {
        "apiVersion": "kpack.io/v1alpha2",
        "kind": "Image",
        "metadata": {
            "name": f"{project.name}-{node.id}-kp-image"
        },
        "spec": {
            "tag": f"{settings.KPACK_DOCKER_REGISTRY}{username}-{project.name}-{node.id}-kp-image",
            "serviceAccountRef": {
                "name": f"{node.id}-sva",
                "namespace": username
            },
            "builder": {
                "name": "default-builder",
                "kind": "ClusterBuilder"
            },
            "source": {}
        }
    }

    if node.node_type == "git":
        revision = node.git_revision
        repo = node.git_repo
        img_obj["spec"]["source"] = {
            "git": {
                "url": repo,
            }
        }
        if revision != "" and revision is not None:
            img_obj["spec"]["source"]["git"]["revision"] = revision
    elif node.node_type == "local":
        airtifact = node.zipped_project
        img_obj["spec"]["source"] = {
            "blob": {
                "url": airtifact
            }
        }

    resp = custom_obj_api.create_namespaced_custom_object(
        group="kpack.io",
        version="v1alpha2",
        namespace=username,
        plural="images",
        body=img_obj,
    )
    print(resp.status)


def create_git_secret(token: str, gh_username: str, node_id, namespace: str):
    git_secret = f"""
apiVersion: v1
kind: Secret
metadata:
  name: {node_id}-gh-secret
  annotations:
    kpack.io/git: https://github.com
type: kubernetes.io/basic-auth
stringData:
  username: {gh_username}
  password: {token}
"""
    di = yaml.load(git_secret, BaseLoader)
    resp = core_api.create_namespaced_secret(namespace, di)


def create_kp_builder(project: Project, node: Node, username: str):
    img = f"""
apiVersion: kpack.io/v1alpha2
kind: Builder
metadata:
  name: {project.name}-{node.id}-builder
spec:
  tag: jimjuniorb/{project.name}-{username}-kp-builder
  serviceAccountName: {project.name}-sva
  stack:
    name: base-stack
    kind: ClusterStack
  store:
    name: default-store
    kind: ClusterStore
  order:
  - group:
    - id: paketo-buildpacks/java
  - group:
    - id: paketo-buildpacks/nodejs
"""
    di = yaml.load(img, BaseLoader)

    resp = custom_obj_api.create_namespaced_custom_object(
        group="kpack.io",
        version="v1alpha2",
        namespace=username,
        plural="builders",
        body=di,
    )
    print(resp.status)


def create_proj_sva(node, namespace: str):

    nodesva_obj = {
        "apiVersion": "v1",
        "kind": "ServiceAccount",
        "metadata": {
            "name": f"{node.id}-sva",
            "namespace": namespace,
            "secrets": [
                {
                    "name": "docker-configjson"
                }
            ],
            "imagePullSecrets": [
                {
                    "name": "docker-configjson"
                }
            ]
        }
    }
    if node.is_public_repo == False:
        nodesva_obj["metadata"]["secrets"].append(
            {
                "name": f"{node.id}-gh-secret"
            }
        )
    resp = core_api.create_namespaced_service_account(namespace, nodesva_obj)
