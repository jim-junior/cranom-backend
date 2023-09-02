import json
from time import sleep
import asyncio
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from threading import Thread
from channels.db import database_sync_to_async
from deployments.models import Project, Node
from deployments.utils.ws_token import decrypt
from kube.config import get_api_client_config
from kubernetes import client, config, watch


async def get_node_logs(obj, node, username):
    """
    Get Logs for a specific node. This should be run in a Thread
    """
    """ apiConfig = get_api_client_config()
    apiclient = client.ApiClient(apiConfig)
    v1 = client.CoreV1Api(apiclient) """
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()

    imageName = f"{node['project']}-{node['id']}-kp-image"
    podname = ""
    pods = v1.list_namespaced_pod(username)
    for pod in pods.items:
        for key, value in pod.metadata.labels.items():
            if key == "image.kpack.io/image":
                if value == imageName:
                    podname = pod.metadata.name
                    break
    
    for e in w.stream(v1.read_namespaced_pod_log, name=podname, namespace=username, container="build" ):
        if e != None:
            obj.send(text_data=json.dumps({
                'message': e,
                "type": "logs"
            }))


class NodeDeploymentProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.node_id = self.scope['url_route']['kwargs']['node_id']
        self.token = self.scope['url_route']['kwargs']['token']
        userObj = decrypt(self.token)
        if userObj["username"] == None:
            await self.close()
        else:
            await self.accept()
            await self.send(text_data=json.dumps({
                'message': "",
                "type": "platfrom",
                "status": "In Queue"
            }))
            await asyncio.sleep(4)
            await self.send(text_data=json.dumps({
                'message': "",
                "type": "platfrom",
                "status": "Building"
            }))

            await asyncio.sleep(4)
            await self.send(text_data=json.dumps({
                'message': "",
                "type": "platfrom",
                "status": "Deploying"
            }))
            await asyncio.sleep(4)
            await self.send(text_data=json.dumps({
                'message': "",
                "type": "platfrom",
                "status": "Deployed"
            }))

    async def disconnect(self, code):
        return await super().disconnect(code)
