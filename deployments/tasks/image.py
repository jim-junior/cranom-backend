from kubernetes import client, config, watch
from kube.config import get_api_client_config


apiConfig = get_api_client_config()
apiclient = client.ApiClient(apiConfig)
v1 = client.CoreV1Api(apiclient)
apps_v1_api = client.AppsV1Api(apiclient)
networking_v1_api = client.NetworkingV1Api(apiclient)

crd_api = client.CustomObjectsApi(apiConfig)


def watch_kp_image(image):
    current = None

    while True:
        obj = crd_api.get_namespaced_custom_object(
            group="kpack.io",
            version="v1alpha2",
            namespace="default",
            plural="images",
            name="image"
        )
        status = obj["status"]["conditions"][0]["status"]
        if status == "True":
            print("Build Passed")
            break
        elif status == "False":
            print("Build Failed")
            break
        else:
            if current is None:
                print("Building")
                current = status
                print(current)
