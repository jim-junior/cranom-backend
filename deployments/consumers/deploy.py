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
    api = client.ApiClient()

    imageName = f"{node['project']}-{node['id']}-kp-image"
    podname = ""
    pods = v1.list_namespaced_pod(username)
    for pod in pods.items:
        for key, value in pod.metadata.labels.items():
            if key == "image.kpack.io/image":
                if value == imageName:
                    podname = pod.metadata.name
                    break
    
    

    podDict = api.sanitize_for_serialization(pod)
    

    while True:
        temp_pod = v1.read_namespaced_pod(name=podname, namespace=username)
        if temp_pod.status.init_container_statuses != None:
            while True:
                status = ""
                pod = v1.read_namespaced_pod(name=podname, namespace=username)
                for container in pod.status.init_container_statuses:
                    if container.name == "build":
                        if container.state.running != None:
                            await obj.send(text_data=json.dumps({
                                    'message': "",
                                    "type": "platfrom",
                                    "status": "Building"
                                }))
                            for e in w.stream(v1.read_namespaced_pod_log, name=podname, namespace=username, container="build" ):
                                
                                await obj.send(text_data=json.dumps({
                                        'message': e,
                                        "type": "buildLogs"
                                    }))
                                
                            status = "Building"
                            break
                        elif container.state.waiting != None:
                            await obj.send(text_data=json.dumps({
                                    'message': "",
                                    "type": "platfrom",
                                    "status": "Preparing"
                                }))
                            status = "Waiting"
                            sleep(1)
                            break
                if status == "Waiting":
                    continue
                else:
                    break
            break
        else:
            print(temp_pod.status)
            await obj.send(text_data=json.dumps({
                'message': "",
                "type": "platfrom",
                "status": "Preparing"
            }))
        sleep(1)

    

    
    await obj.send(text_data=json.dumps({
        'message': "",
        "type": "platfrom",
        "status": "Deploying"
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
            await asyncio.sleep(2)
            nodeInfo = await self.get_node_info()
            if nodeInfo["exists"] == True:
                

                logging_thread = Thread(target=self.between_callback, args=(
                    nodeInfo, userObj["username"],))
                logging_thread.start()
            else:
                await self.send(text_data=json.dumps({
                    'message': "",
                    "type": "platfrom",
                    "status": "Failed"
                }))
                print("Node does not exists")


    async def disconnect(self, code):
        return await super().disconnect(code)

    @database_sync_to_async
    def get_node_info(self):
        node_id = self.node_id
        if Node.objects.filter(pk=node_id).exists():
            node = Node.objects.get(pk=node_id)
            project = node.project
            nodeInfo = {
                "exists": True,
                "running": node.running,
                "name": node.name,
                "id": node.id,
                "project": project.name,
            }
            return nodeInfo
        else:
            return {
                "exists": False
            }


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.logging = False

    def between_callback(self, node, username):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(get_node_logs(self, node, username))
        loop.close()
