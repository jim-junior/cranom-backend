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


def create_service_account(user, name):
    body = client.V1ServiceAccount(
        metadata=client.V1ObjectMeta(
            name=f"{name}-service-account",
            namespace=user
        )
    )

    api_response = v1.create_namespaced_service_account(
        body=body,
        namespace=user
    )
    print("Service account created with status")


def create_role_binding(user, name):
    body = client.V1RoleBinding(
        metadata=client.V1ObjectMeta(
            name=f"{name}-role-binding",
            namespace=user
        ),
        role_ref=client.V1RoleRef(
            api_group="rbac.authorization.k8s.io",
            kind="Role",
            name="admin"
        ),
        subjects=[
            client.V1Subject(
                kind="ServiceAccount",
                name=f"{name}-service-account",
                namespace=user
            )
        ]
    )

    api_response = v1.create_namespaced_role_binding(
        body=body,
        namespace=user
    )
    print("Role binding created with status")


def create_role(user, name):
    body = client.V1Role(
        metadata=client.V1ObjectMeta(
            name=f"{name}-role",
            namespace=user
        ),
        rules=[
            client.V1PolicyRule(
                api_groups=[
                    "*"
                ],
                resources=[
                    "*"
                ],
                verbs=[
                    "*"
                ]
            )
        ]
    )

    api_response = v1.create_namespaced_role(
        body=body,
        namespace=user
    )
    print("Role created with status")


def create_secret(user, name, token):
    body = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name=f"{name}-secret",
            namespace=user
        ),
        data={
            "token": token
        }
    )

    api_response = v1.create_namespaced_secret(
        body=body,
        namespace=user
    )
    print("Secret created with status")


def create_service_account_token_secret(user, name):
    body = client.V1Secret(
        metadata=client.V1ObjectMeta(
            name=f"{name}-service-account-token-secret",
            namespace=user
        ),
        data={
            "token": "token"
        }
    )

    api_response = v1.create_namespaced_secret(
        body=body,
        namespace=user
    )
    print("Secret created with status")


def create_service_account_token_secret_binding(user, name):
    body = client.V1SecretReference(
        name=f"{name}-service-account-token-secret",
        namespace=user
    )

    api_response = v1.create_namespaced_service_account_token_secret_reference(
        body=body,
        namespace=user
    )
    print("Secret reference created with status")


def create_service_account_token_secret_binding_binding(user, name):
    body = client.V1ServiceAccountTokenProjection(
        audience="audience",
        service_account_name=f"{name}-service-account"
    )

    api_response = v1.create_namespaced_service_account_token_secret_reference(
        body=body,
        namespace=user
    )
    print("Secret reference created with status")
