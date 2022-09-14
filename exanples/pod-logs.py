from kubernetes import client, config, watch


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    v1 = client.CoreV1Api()
    count = 10
    w = watch.Watch()
    v1 = client.CoreV1Api()
    #w = Watch()
    for e in w.stream(v1.read_namespaced_pod_log, name="hello-node-deployment-6568bdf595-mktj9", namespace="default"):
        print(e)


if __name__ == '__main__':
    main()
