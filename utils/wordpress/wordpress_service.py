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

WORDPRESS_SECRET_YML = """
apiVersion: v1
kind: Service
metadata:
  name: word-service
spec:
  selector:
    app: word-dep
  ports:
  - port: 80
    targetPort: 80
    nodePort: 31001
  type: NodePort
"""


def create_wordpress_service():
    body = client.V1Service(
        metadata=client.V1ObjectMeta(
            name="word-service",
            namespace="default"
        ),
        spec=client.V1ServiceSpec(
            selector={
                "app": "word-dep"
            },
            ports=[
                client.V1ServicePort(
                    port=80,
                    target_port=80,
                    node_port=31001
                )
            ],
            type="NodePort"
        )
    )

    api_response = v1.create_namespaced_service(
        body=body,
        namespace="default"
    )
    print("Service created with status")
