from kubernetes import client, config, watch
import json


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    print("hello")
    config.load_kube_config()

    v1 = client.CoreV1Api()

    api = client.ApiClient()
    #w = Watch()
    pods = v1.list_namespaced_pod("pxyxrlyuvl")
    for pod in pods.items:
        di = api.sanitize_for_serialization(pod)
        # write to file
        with open("pod.json", "w") as f:
            jsonoj = json.dumps(di, indent=4)
            f.write(jsonoj)

    # change p to a dict



if __name__ == '__main__':
    main()
