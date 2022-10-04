import json
import httpx
from kubernetes import client, config
from kube.config import get_api_client_config
import yaml
from yaml.loader import BaseLoader
from ...models import Deployment, Project

apiConfig = get_api_client_config()
apiclient = client.ApiClient(apiConfig)

api = client.CustomObjectsApi(apiclient)


def create_kp_image(project: Project, deployment: Deployment, username: str):
    img = f"""
apiVersion: kpack.io/v1alpha2
kind: Image
metadata:
  name: {project.name}-kp-image
  namespace: default
spec:
  tag: jimjuniorb/{project.name}-kp-image
  serviceAccountRef:
    name: kpack-sva
    namespace: default
  builder:
    name: default-builder
    kind: ClusterBuilder
  source:
"""
    di = yaml.load(img, BaseLoader)

    if project.project_type == "git":
        revision = deployment.git_revision
        repo = project.git_repo
        di["spec"]["source"] = {
            "git": {
                "url": repo,
                "revision": revision
            }
        }
    elif project.project_type == "local":
        airtifact = deployment.zipped_project
        di["spec"]["source"] = {
            "blob": {
                "url": airtifact
            }
        }

    resp = api.create_namespaced_custom_object(
        group="kpack.io",
        version="v1alpha2",
        namespace="default",
        plural="images",
        body=di,
    )
    print(resp.status)
