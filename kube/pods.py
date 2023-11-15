from deployments.models import Node
from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()


def get_node_pod(node: Node) -> str | None:
    deployment = f"{node.name}-{node.pk}"
    namespace = node.project.user.username

    pods = v1.list_namespaced_pod(namespace=namespace)
    for pod in pods.items:
        if pod.metadata.name.startswith(deployment):
            return pod.metadata.name
    return None
