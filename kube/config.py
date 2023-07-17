from kubernetes import client, config
from django.conf import settings


def get_api_client_config():
    aToken = settings.KUBE_CLUSTER_TOKEN

    aConfiguration = client.Configuration()

    aConfiguration.host = settings.KUBE_CLUSTER_HOST

    aConfiguration.verify_ssl = False
    aConfiguration.api_key = {"authorization": "Bearer " + aToken}

    return aConfiguration
