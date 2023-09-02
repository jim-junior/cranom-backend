import json
from time import sleep
import asyncio
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from threading import Thread
from channels.db import database_sync_to_async
from deployments.models import Project, Node
from deployments.utils.ws_token import decrypt
from kube.config import get_api_client_config


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
