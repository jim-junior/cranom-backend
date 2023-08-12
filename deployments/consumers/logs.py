import json
from time import sleep
import asyncio
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from kubernetes import client, config, watch
from threading import Thread
from channels.db import database_sync_to_async
from deployments.models import Project, Node
from deployments.utils.ws_token import decrypt
from kube.config import get_api_client_config
import asyncio


def get_logs(obj, name, nodeId, username):
    """ apiConfig = get_api_client_config()
    apiclient = client.ApiClient(apiConfig)
    v1 = client.CoreV1Api(apiclient) """
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()
    depname = f"{name}-{nodeId}"
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

    deploymentName = f"{node['name']}-{node['id']}-deployment"
    podname = ""
    pods = v1.list_namespaced_pod(username)
    for pod in pods.items:
        if pod.metadata.labels["app"] == deploymentName:
            podname = pod.metadata.name
            break
    for e in w.stream(v1.read_namespaced_pod_log, name=podname, namespace=username, tail_lines=6):

        if obj.logging == True:
            await obj.sendMessage(e)
        else:
            w.stop()


class NodeLogsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.node_id = self.scope['url_route']['kwargs']['node_id']
        self.token = self.scope['url_route']['kwargs']['token']
        userObj = decrypt(self.token)
        if userObj["username"] == None:
            await self.close()
        else:
            await self.accept()
            nodeInfo = await self.get_node_info()
            if nodeInfo["exists"] == True:
                if nodeInfo["running"] == True:
                    self.logging = True
                    # Open new thread to watch and send pod logs
                    # This is because running it directly in the consumer will block the consumer
                    logging_thread = Thread(target=self.between_callback, args=(
                        nodeInfo, userObj["username"],))
                    logging_thread.start()
                    """ await self.send(text_data=json.dumps({
                        'message': "CRANOM::: Node is not Running"
                    })) """

                else:
                    await self.send(text_data=json.dumps({
                        'message': "Node is not Running"
                    }))
                    await self.close()
            else:
                await self.send(text_data=json.dumps({
                    'message': "Node does not Exists"
                }))
                await self.close()

    async def sendMessage(self, message):
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_node_info(self):
        node_id = self.node_id
        if Node.objects.filter(pk=node_id).exists():
            node = Node.objects.get(pk=node_id)
            nodeInfo = {
                "exists": True,
                "running": node.running,
                "name": node.name,
                "id": node.id
            }
            return nodeInfo
        else:
            return {
                "exists": False
            }

    async def disconnect(self, close_code):
        if self.logging == True:
            self.logging = False
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.logging = False

    def between_callback(self, node, username):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(get_node_logs(self, node, username))
        loop.close()
