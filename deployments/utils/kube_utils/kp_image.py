import json
import httpx
from kubernetes import client, config
from kube.config import get_api_client_config
import yaml
from yaml.loader import BaseLoader
from ...models import Deployment, Project, Node
from django.conf import settings

apiConfig = get_api_client_config()
apiclient = client.ApiClient(apiConfig)

custom_obj_api = client.CustomObjectsApi(apiclient)
core_api = client.CoreV1Api(apiclient)


def create_kp_image(project: Project, node: Node, username: str):
    img = f"""
apiVersion: kpack.io/v1alpha2
kind: Image
metadata:
  name: {project.name}-{node.id}-kp-image
  namespace: default
spec:
  tag: {settings.KPACK_DOCKER_REGISTRY}{username}-{project.name}-{node.id}-kp-image
  serviceAccountRef:
    name: kpack-sva
    namespace: default
  builder:
    name: default-builder
    kind: ClusterBuilder
  source:
"""
    di = yaml.load(img, BaseLoader)

    if node.node_type == "git":
        revision = node.git_revision
        repo = node.git_repo
        di["spec"]["source"] = {
            "git": {
                "url": repo,
                "revision": revision
            }
        }
    elif node.node_type == "local":
        airtifact = node.zipped_project
        di["spec"]["source"] = {
            "blob": {
                "url": airtifact
            }
        }

    resp = custom_obj_api.create_namespaced_custom_object(
        group="kpack.io",
        version="v1alpha2",
        namespace=username,
        plural="images",
        body=di,
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
  - group:
    - id: kpack/my-custom-buildpack
      version: 1.2.3
    - id: kpack/my-optional-custom-buildpack
      optional: true
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


def create_proj_sva(project, node, namespace: str):
    proj_sva = f"""
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {node.id}-sva
  namespace: {namespace}
secrets:
- name: docker-configjson
- name: {node.id}-gh-secret
imagePullSecrets:
- name: docker-configjson
"""
    di = yaml.load(proj_sva, BaseLoader)
    resp = core_api.create_namespaced_service_account(namespace, di)
