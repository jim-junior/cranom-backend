from kubernetes import client, config, watch


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    w = watch.Watch()
    v1 = client.CoreV1Api()
    #w = Watch()
    p = v1.read_namespaced_pod(
        name="tutorial-image-3-build-8-build-pod", namespace="default")
    print(p)


if __name__ == '__main__':
    main()
