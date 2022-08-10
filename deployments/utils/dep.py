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
