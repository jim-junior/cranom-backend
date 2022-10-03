
import time

from kubernetes import config, client


name = 'nodeapp-deployment-784d8dc7b6-lj5tm'
config.load_kube_config()
v1 = client.CoreV1Api()

v1.connect_get_namespaced_pod_exec(name,
                                   'cli',
                                   command='/bin/sh',
                                   stderr=True,
                                   stdin=True,
                                   stdout=True,
                                   tty=True)
