import json
import httpx
from kubernetes import client, config
from kube.config import get_api_client_config
from deployments.models import Deployment, Project, Node, DomainName
from users.models import UserProfile
from django.conf import settings

""" apiConfig = get_api_client_config()
apiclient = client.ApiClient(apiConfig)
v1 = client.CoreV1Api(apiclient)
apps_v1_api = client.AppsV1Api(apiclient)
networking_v1_api = client.NetworkingV1Api(apiclient) """

config.load_kube_config()
v1 = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()
networking_v1_api = client.NetworkingV1Api()


def create_git_node_deployment(node: Node):
    envs = node.env_variables
    name = node.name
    project: Project = node.project
    user: UserProfile = project.user

    # Get Docker Image
    docker_image = ""
    if node.node_type == "docker":
        docker_image = node.image
    else:
        docker_image = f"{settings.KPACK_DOCKER_REGISTRY}{user.username}-{project.name}-{node.id}-kp-image"

    # Get Environment Variables
    environVars = []
    for var in envs:
        environVars.append(
            client.V1EnvVar(
                name=var["name"],
                value=var["value"]
            )
        )

    # Generate Container Configuration
    container = {
        "name": f"{node.name}-{node.id}",
        "image": docker_image,
        "imagePullPolicy": "Never",
        "env": environVars
    }

    if node.process_type == "web":
        container["ports"] = [
            {
                "name": f"{project.name}-{node.id}-port",
                "containerPort": node.port
            }
        ]

    dic = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{name}-{node.id}-deployment",
            "labels": {
                "app": f"{name}-{node.id}-deployment"
            }
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": f"{name}-{node.id}-deployment"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": f"{name}-{node.id}-deployment"
                    }
                },
                "spec": {
                    "containers": [container]
                }
            }
        }
    }

    if node.running == True:
        try:
            respo = apps_v1_api.patch_namespaced_deployment(
                namespace=user.username, body=dic
            )
            node.build_status = "Success"
            node.save()
            print(
                f"Deployed {node.name} {node.id} successefuly"
            )
        except:
            node.build_status = "Failed"
            node.save()
            print(
                f"FAILED: {node.name} {node.id} failed to deploy"
            )
    else:

        try:
            api_response = apps_v1_api.create_namespaced_deployment(
                body=dic,
                namespace=user.username
            )
            if api_response.status == "Success":
                node.build_status = "Success"
                node.save()
            node.build_status = "Success"
            node.save()
            print(
                f"Deployed {node.name} {node.id} successefuly"
            )
        except:
            node.build_status = "Failed"
            node.save()
            print(
                f"FAILED: {node.name} {node.id} failed to deploy"
            )


def create_git_node_service(node: Node):
    # Get node Metadata
    print(node)
    print(node.name)
    print(node.port)
    name = node.name
    project: Project = node.project
    user: UserProfile = project.user

    body = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=f"{name}-{node.id}-service",
        ),
        spec=client.V1ServiceSpec(
            selector={
                "app": f"{name}-{node.id}-deployment"
            },
            ports=[
                client.V1ServicePort(
                    port=node.port,
                    target_port=f"{project.name}-{node.id}-port",
                    # protocol=node.network_protocol
                )
            ],
            # type="LoadBalancer"
        )
    )

    if node.running == True:
        v1.patch_namespaced_service(
            namespace=user.username,
            body=body
        )
        print("Service patched")
    else:
        api_response = v1.create_namespaced_service(
            body=body,
            namespace=user.username
        )
        print(f"Service created. status='{api_response.status}'")


def create_node_ingress(node: Node):
    name = node.name
    project: Project = node.project
    user: UserProfile = project.user

    ing_obj = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": f"{name}-{user.username}-ingress",
            "annotations": {
                "kubernetes.io/ingress.class": "nginx",
                "external-dns.alpha.kubernetes.io/hostname": f"{name}-{user.username}.{settings.APP_DEPLOYMENTS_DOMAIN}"
            }
        },
        "spec": {
            "rules": [
                {
                    "host": f"{name}-{node.id}.{settings.APP_DEPLOYMENTS_DOMAIN}",
                    "http": {
                        "paths": [
                            {
                                "pathType": "Prefix",
                                "path": "/",
                                "backend": {
                                    "service": {
                                        "name": f"{name}-{node.id}-service",
                                        "port": {
                                            "number": node.port
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    try:

        if node.running == True:
            api_response = networking_v1_api.patch_namespaced_ingress(
                name=f"{name}-{user}-ingress",
                body=ing_obj,
                namespace=user
            )
            domainName = f"{name}-{user}.{settings.APP_DEPLOYMENTS_DOMAIN}"
            domain = DomainName.objects.create(
                name=domainName,
                project=project.project_uuid,
                node=node.pk
            )
            domain.save()
        else:
            api_response = networking_v1_api.create_namespaced_ingress(
                body=ing_obj,
                namespace=user
            )

    except:
        pass


def delete_git_node_deployment(node: Node):
    name = node.name
    project: Project = node.project
    user: UserProfile = project.user

    try:
        api_response = apps_v1_api.delete_namespaced_deployment(
            name=f"{name}-{node.id}-deployment",
            namespace=user.username
        )
        node.running = False
        node.save()
    except:
        node.running = False
        node.save()


def delete_git_node_service(node: Node):
    name = node.name
    project: Project = node.project
    user: UserProfile = project.user

    try:
        api_response = v1.delete_namespaced_service(
            name=f"{name}-{node.id}-service",
            namespace=user.username
        )
    except:
        pass


def delete_git_node_ingress(node: Node):
    name = node.name
    project: Project = node.project
    user: UserProfile = project.user

    try:
        api_response = networking_v1_api.delete_namespaced_ingress(
            name=f"{name}-{user.username}-ingress",
            namespace=user.username
        )
    except:
        pass
