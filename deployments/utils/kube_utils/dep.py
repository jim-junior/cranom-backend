import json
import httpx
from kubernetes import client, config
from kube.config import get_api_client_config

apiConfig = get_api_client_config()
apiclient = client.ApiClient(apiConfig)
v1 = client.CoreV1Api(apiclient)
apps_v1_api = client.AppsV1Api(apiclient)
networking_v1_api = client.NetworkingV1Api(apiclient)

""" config.load_kube_config()
v1 = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()
networking_v1_api = client.NetworkingV1Api() """


def create_deployment(user, name, image, port, envs=[], deployed=False):
    print(
        f"Creating deployment {name} for {user}. Deployed: {deployed}, Port: {port}")
    environVars = []
    for var in envs:
        environVars.append(
            client.V1EnvVar(
                name=var["name"],
                value=var["value"]
            )
        )

    dic = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{name}-deployment",
            "labels": {
                "app": f"{name}-deployment"
            }
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": f"{name}-deployment"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": f"{name}-deployment"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": f"{name}-containor",
                            "image": image,
                            "imagePullPolicy": "Always",
                            "ports": [
                                {
                                    "name": f"{name}-port",
                                    "containerPort": 3000
                                }
                            ],
                            "env": environVars
                        }
                    ]
                }
            }
        }
    }

    if deployed == True:
        respo = apps_v1_api.patch_namespaced_deployment(
            name=f"{name}-deployment", namespace=user, body=dic
        )
    else:
        api_response = apps_v1_api.create_namespaced_deployment(
            body=dic,
            namespace=user
        )


def create_service(name, port, user, deployed):
    print(
        f"Creating SVC {name} for {user}. Deployed: {deployed}, Port: {port}")
    body = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=f"{name}-service",
        ),
        spec=client.V1ServiceSpec(
            selector={
                "app": f"{name}-deployment"
            },
            ports=[
                client.V1ServicePort(
                    port=port,
                    target_port=port,
                )
            ],
            # type="LoadBalancer"
        )
    )
    print(f">>>>>>>>>>> {user}")

    if deployed == True:
        v1.patch_namespaced_service(
            name=f"{name}-service",
            namespace=user,
            body=body
        )
        print("Service patched")
    else:
        api_response = v1.create_namespaced_service(
            body=body,
            namespace=user
        )
        print(f"Service created. status='{api_response.status}'")


def create_ingress(name, port, user, deployed):
    print(
        f"Creating Ingress {name} for {user}. Deployed: {deployed}, Port: {port}")
    ing_obj = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": f"{name}-{user}-ingress",
            "annotations": {
                "kubernetes.io/ingress.class": "nginx",
                "external-dns.alpha.kubernetes.io/hostname": f"{name}-{user}.cranomapp.ml"
            }
        },
        "spec": {
            "rules": [
                {
                    "host": f"{name}-{user}.cranomapp.ml",
                    "http": {
                        "paths": [
                            {
                                "pathType": "Prefix",
                                "path": "/",
                                "backend": {
                                    "service": {
                                        "name": f"{name}-service",
                                        "port": {
                                            "number": port
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

    if deployed == True:
        api_response = networking_v1_api.patch_namespaced_ingress(
            name=f"{name}-{user}-ingress",
            body=ing_obj,
            namespace=user
        )
    else:
        api_response = networking_v1_api.create_namespaced_ingress(
            body=ing_obj,
            namespace=user
        )
