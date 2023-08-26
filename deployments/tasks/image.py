from kubernetes import client, config, watch
from kube.config import get_api_client_config
from deployments.models import Node
from deployments.utils.kube_utils.git_deployment import create_git_node_deployment, create_git_node_service, create_node_ingress
from celery import shared_task


""" apiConfig = get_api_client_config()
apiclient = client.ApiClient(apiConfig)
v1 = client.CoreV1Api(apiclient)
apps_v1_api = client.AppsV1Api(apiclient)
networking_v1_api = client.NetworkingV1Api(apiclient)

crd_api = client.CustomObjectsApi(apiConfig) """

config.load_kube_config()
v1 = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()
networking_v1_api = client.NetworkingV1Api()
crd_api = client.CustomObjectsApi()


@shared_task()
def deploy_kp_image(nodeid):
    node = Node.objects.get(id=nodeid)
    project = node.project
    user = project.user

    current = None

    while True:
        obj = crd_api.get_namespaced_custom_object(
            group="kpack.io",
            version="v1alpha2",
            namespace=user.username,
            plural="images",
            name=f"{project.name}-{node.id}-kp-image"
        )
        # Get Kpack image build status
        status = obj["status"]["conditions"][0]["status"]
        if status == "True":
            # Deploy to kubernetes
            create_git_node_deployment(node)
            create_git_node_service(node)
            create_node_ingress(node)
            break
        elif status == "False":
            node.build_status = "Failed"
            node.save()
            break
        else:
            if current is None:
                current = status
                node.build_status = "Building"
                node.save()
