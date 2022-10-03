from kubernetes import client, config, watch


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    w = watch.Watch()
    v1 = client.CoreV1Api()
    #w = Watch()
    for e in w.stream(v1.read_namespaced_pod_log, name="nodeapp-deployment-784d8dc7b6-lj5tm", namespace="cli", tail_lines=1):
        print(e)


if __name__ == '__main__':
    main()
