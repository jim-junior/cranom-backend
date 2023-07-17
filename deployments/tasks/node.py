from deployments.utils.kube_utils.git_deployment import (
    create_git_node_deployment,
    create_git_node_service,
    create_node_ingress,
    delete_git_node_deployment,
    delete_git_node_ingress,
    delete_git_node_service
)
from celery import shared_task
from deployments.models import Node


def deploy_node(node_id):
    node = Node.objects.get(id=node_id)
    node.build_status = "started"
    node.save()
    create_git_node_deployment(node)
    create_git_node_service(node)
    # create_node_ingress(node)
    node.running = True
    node.save()
