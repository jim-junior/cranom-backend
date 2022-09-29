import json
from time import sleep
from channels.generic.websocket import WebsocketConsumer
from kubernetes import client, config, watch
from threading import Thread


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


class LogingConsumer(WebsocketConsumer):
    def connect(self):
        self.proj_uuid = self.scope['url_route']['kwargs']['uuid']
        self.accept()
        sleep(1)
        self.send(text_data=json.dumps({
            'message': "Connected to Project logs Successfully"
        }))
        self.logging = True
        logging_thread = Thread(target=get_logs, args=(self,))
        logging_thread.start()

    def disconnect(self, close_code):
        if self.logging == True:
            self.logging = False
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.logging = False

    def get_project_info(self, uuid):
        pass
