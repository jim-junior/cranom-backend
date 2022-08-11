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


def create_deployment(user, name, image, version, port, envs):
    environVars = []

    for var in envs:
        environVars.append(
            client.V1EnvVar(
                name=var["name"],
                value=var["value"]
            )
        )
    body = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=f"{name}-deployment"),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector={"matchLabels": {"app": f"{name}-deployment"}},
            template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": f"{name}-deployment"}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=f"{name}-deployment",
                                image=f"{image}:{version}",
                                ports=[client.V1ContainerPort(
                                    container_port=port)],
                                image_pull_policy="IfNotPresent",
                                env=environVars
                            ),
                        ]
                    )
            )
        )
    )

    api_response = apps_v1_api.create_namespaced_deployment(
        body=body,
        namespace=user
    )


def create_service(name, port, user):
    body = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=f"{name}-service",
            namespace="default"
        ),
        spec=client.V1ServiceSpec(
            selector={
                "app": f"{name}-deployment"
            },
            ports=[
                client.V1ServicePort(
                    port=port,
                    target_port=port,
                    node_port=31001
                )
            ],
            type="NodePort"
        )
    )

    api_response = v1.create_namespaced_service(
        body=body,
        namespace=user
    )
    print("Service created with status")


def create_ingress(name, port, user):
    body = client.V1beta1Ingress(
        metadata=client.V1ObjectMeta(
            name=f"{name}-ingress",
            namespace="default"
        ),
        spec=client.V1beta1IngressSpec(
            rules=[
                client.V1beta1IngressRule(
                    host=f"{name}.cranom.ml",
                    http=client.V1beta1HTTPIngressRuleValue(
                        paths=[
                            client.V1beta1HTTPIngressPath(
                                backend=client.V1beta1IngressBackend(
                                    service_name=f"{name}-service",
                                    service_port=port
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )

    api_response = networking_v1_api.create_namespaced_ingress(
        body=body,
        namespace=user
    )
    print("Ingress created with status")


def get_deployment_logs(name, user):
    api_response = v1.read_namespaced_deployment_log(
        name=f"{name}-deployment",
        namespace=user
    )
    return api_response.body
