from kubernetes import client, config, watch
import json


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    w = watch.Watch()
    v1 = client.CoreV1Api()
    #w = Watch()
    podname = ""
    pods = v1.list_namespaced_pod("ehhazxowda")
    for pod in pods.items:
        for key, value in pod.metadata.labels.items():
            if key == "image.kpack.io/image":
                podname = pod.metadata.name
                break
    # change p to a dict
    print(podname)



if __name__ == '__main__':
    main()
