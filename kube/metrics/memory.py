from deployments.models import Node
import httpx
from kube.pods import get_node_pod

PROMETHEUS_URL = "127.0.0.1:9090"


def get_node_memory_usage(node: Node, hours: int) -> str | None:
    try:
        namespace = node.project.user.username
        pod = "mydb-1-56fd9744fd-7vrh7"
        # pod = get_node_pod(node)
        if pod is None:
            return None
        query = 'container_memory_usage_bytes{namespace="' + \
            "qjnvahegmv" + '", pod="' + pod + '"}[' + str(hours) + 'h]'
        url = "http://" + PROMETHEUS_URL + "/api/v1/query"
        params = {
            "query": query
        }
        r = httpx.get(url, params=params)
        return r.json()
    except:
        return None
