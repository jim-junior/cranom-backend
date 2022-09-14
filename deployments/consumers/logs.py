import json
from time import sleep
from channels.generic.websocket import WebsocketConsumer
from kubernetes import client, config, watch
#from celery import shared_task


def get_logs(obj):
    config.load_kube_config()
    w = watch.Watch()
    v1 = client.CoreV1Api()
    for e in w.stream(v1.read_namespaced_pod_log, name="hello-node-deployment-6568bdf595-mktj9", namespace="default"):
        if obj.logging == True:
            obj.send(text_data=json.dumps({
                'message': e
            }))
        else:
            w.stop()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        sleep(1)
        self.send(text_data=json.dumps({
            'message': "Restarting App with PID"
        }))
        self.logging = True
        #get_logs.delay(self)
        # self.get_logs()

    def disconnect(self, close_code):
        print("Stoppind")
        # self.watcher.stop()
        print("stopped")
        pass

    def receive(self, text_data):
        print("REcieveing")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.logging = False

        print(message)

    def get_logs(self):
        config.load_kube_config()
        w = watch.Watch()
        v1 = client.CoreV1Api()
        for e in w.stream(v1.read_namespaced_pod_log, name="hello-node-deployment-6568bdf595-mktj9", namespace="default"):
            if self.logging == True:
                self.send(text_data=json.dumps({
                    'message': e
                }))
            else:
                w.stop()
