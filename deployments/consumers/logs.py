import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ..models import DockerDeployment

from kubernetes import client, config, watch

try:
    config.load_incluster_config()
    print("Loaded cluster config")
except config.config_exception.ConfigException:
    config.load_kube_config()


v1 = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()
networking_v1_api = client.NetworkingV1Api()
w = watch.Watch()

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))


# A consumer that streams the logs of a given docker deployment to the browser through websockets. Each time the container logs are updated, the browser is notified. it uses the kubernetes client to get the logs of the deployment. The logs are streamed to the browser. The kubernetes deployment name is passed as a parameter to the consumer.
class LogsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.deployment_name = self.scope['url_route']['kwargs']['deployment']
        self.deployment = DockerDeployment.objects.get(name=self.deployment_name)
        self.deployment.logs = ""
        self.deployment.save()
        await self.channel_layer.group_add(
            self.deployment_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.deployment_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.deployment_name,
            {
                'type': 'logs_message',
                'message': message
            }
        )

    async def logs_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))