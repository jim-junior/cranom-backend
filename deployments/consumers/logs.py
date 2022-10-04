import json
from time import sleep

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from kubernetes import client, config, watch
from threading import Thread
from channels.db import database_sync_to_async
from deployments.models import Project
from deployments.utils.ws_token import decrypt
from kube.config import get_api_client_config


def get_logs(obj, name, username):
    apiConfig = get_api_client_config()
    apiclient = client.ApiClient(apiConfig)
    v1 = client.CoreV1Api(apiclient)
    w = watch.Watch()
    depname = name + "-deployment"
    podname = ""
    pods = v1.list_namespaced_pod(username)
    for pod in pods.items:
        if pod.metadata.labels["app"] == depname:
            podname = pod.metadata.name
            break

    for e in w.stream(v1.read_namespaced_pod_log, name=podname, namespace=username, tail_lines=6):
        if obj.logging == True:
            obj.send(text_data=json.dumps({
                'message': e
            }))
        else:
            w.stop()


class LogingConsumer(WebsocketConsumer):
    def connect(self):
        self.proj_uuid = self.scope['url_route']['kwargs']['uuid']
        self.token = self.scope['url_route']['kwargs']['token']
        userObj = decrypt(self.token)
        if userObj["username"] == None:
            self.close()
        else:
            self.accept()
            proj = self.get_project_info()
            print(proj)
            if proj["exists"] == True:
                if proj["deployed"] == True:
                    self.logging = True
                    logging_thread = Thread(target=get_logs, args=(
                        self, proj["name"], userObj["username"],))
                    logging_thread.start()
                else:
                    self.send(text_data=json.dumps({
                        'message': "Project Has Not yet been Deployed"
                    }))
                    self.close()
            else:
                self.send(text_data=json.dumps({
                    'message': "Project does not Exists"
                }))
                self.close()

    def disconnect(self, close_code):
        if self.logging == True:
            self.logging = False
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.logging = False

    def get_project_info(self):
        proj = self.get_obj()
        if proj is not None:
            print(proj)
            return {
                "exists": True,
                "name": proj.name,
                "deployed": proj.deployed
            }
        else:
            return {
                "exists": False
            }

    def get_obj(self):
        uuid = self.proj_uuid
        if Project.objects.filter(project_uuid=uuid).exists():
            proj = Project.objects.get(project_uuid=uuid)
            return proj
        return None
