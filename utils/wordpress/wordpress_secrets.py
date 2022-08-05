import json
import httpx
from kubernetes import client, config
import base64

try:
    config.load_incluster_config()
    print("Loaded cluster config")
except config.config_exception.ConfigException:
    config.load_kube_config()


v1 = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()
networking_v1_api = client.NetworkingV1Api()

WORD_SECRETS_YML = """
apiVersion: v1
kind: Secret
metadata:  
  name: word-secrets
type: Opaque
data:
  dbusername: dXNlcm5hbWUK
  dbpassword: cGFzc3dvcmQK
"""


def create_wordpress_secrets():
    body = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name="word-secrets",
            namespace="default"
        ),
        type="Opaque",
        data={
            "dbusername": base64.b64encode(b"username").decode("utf-8"),
            "dbpassword": base64.b64encode(b"password").decode("utf-8")
        }
    )

    api_response = v1.create_namespaced_secret(
        body=body,
        namespace="default"
    )
    print("Secrete created with status: ")
