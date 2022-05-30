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


def createDeployment(name, image, replicas, port, namespace):
    body = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector={"matchLabels": {"app": name}},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": name}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=name,
                            image=image,
                            ports=[client.V1ContainerPort(
                                container_port=port)],
                            image_pull_policy="Never",
                        )
                    ]
                )
            )
        )
    )

    # Create Deployment
    api_response = apps_v1_api.create_namespaced_deployment(
        body=body, namespace="default")
    print("Deployment created. status='%s'" % str(api_response.status))


def createService(name, port, namespace):
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1ServiceSpec(
            ports=[client.V1ServicePort(port=port)],
            selector={"app": name}
        )
    )

    # Create Service
    api_response = v1.create_namespaced_service(
        body=body, namespace="default")
    print("Service created. status='%s'" % str(api_response.status))
