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


WORDPRESS_DEPLOYMENT_YML = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress-deployment
spec:
  selector:
    matchLabels:
      app: word-dep
  template:
    metadata:
      labels:
        app: word-dep
    spec:
      containers:
      - name: word-dep
        image: wordpress:6.0.0-php7.4-apache
        ports:
        - containerPort: 80
        env:
          - name: WORDPRESS_DB_HOST
            value: mysql-port
          - name: WORDPRESS_DB_PASSWORD
            valueFrom:
              secretKeyRef:
                key: dbpassword
                name: word-secrets
      - name: mysql
        image: mysql:8.0
        ports:
          - name: mysql-port
            containerPort: 3306
        env:
          - name: MYSQL_ROOT_PASSWORD
            valueFrom:
              secretKeyRef:
                key: dbpassword
                name: word-secrets

"""


def create_wordpress_deployment_with_mysql():
    body = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="wordpress-deployment"),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector={"matchLabels": {"app": "wordpress-deployment"}},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": "wordpress-deployment"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="wordpress-deployment",
                            image="wordpress:6.0.0-php7.4-apache",
                            ports=[client.V1ContainerPort(
                                container_port=80)],
                            #image_pull_policy="IfNotPresent",
                            env=[
                                client.V1EnvVar(
                                    name="WORDPRESS_DB_HOST",
                                    value="mysql-port"
                                ),
                                client.V1EnvVar(
                                    name="WORDPRESS_DB_PASSWORD",
                                    value_from=client.V1EnvVarSource(
                                        secret_key_ref=client.V1SecretKeySelector(
                                            key="dbpassword",
                                            name="word-secrets"
                                        )
                                    )
                                )
                            ]
                        ),
                        client.V1Container(
                            name="mysql",
                            image="mysql:8.0",
                            ports=[client.V1ContainerPort(
                                container_port=3306)],
                            #image_pull_policy="IfNotPresent",
                            env=[
                                client.V1EnvVar(
                                    name="MYSQL_ROOT_PASSWORD",
                                    value_from=client.V1EnvVarSource(
                                        secret_key_ref=client.V1SecretKeySelector(
                                            key="dbpassword",
                                            name="word-secrets"
                                        )
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )

    # Create Deployment
    api_response = apps_v1_api.create_namespaced_deployment(
        body=body, namespace="default")
    print("Deployment created. status")


def get_wordpress_deployment():
    # Get Deployment
    api_response = apps_v1_api.read_namespaced_deployment(
        name="wordpress-deployment",
        namespace="default")
    print("Deployment read. status='%s'" % str(api_response.status))


def get_wordpress_pods():
    # Get Deployment
    api_response = v1.list_namespaced_pod(
        namespace="default",
        label_selector="app=wordpress-deployment"
    )
    print("Pods read. status='%s'" % str(api_response.status))


def get_wordpress_pod_logs():
    # Get Deployment
    api_response = v1.list_namespaced_pod(
        namespace="default",
        label_selector="app=wordpress-deployment"
    )
    print("Pods read. status")

    for pod in api_response.items:
        print("Logs for pod '%s'" % pod.metadata.name)
        print(v1.read_namespaced_pod_log(
            name=pod.metadata.name,
            namespace="default",
            container="wordpress-deployment"
        ))
