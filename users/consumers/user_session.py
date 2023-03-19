import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from threading import Thread
from channels.db import database_sync_to_async
from deployments.models import Project, Node
from users.utils.ws_auth import is_token_valid, getUser


class UserSession(AsyncWebsocketConsumer):
    """
    A WebSocket comsumer that is incharge of reporting events to user in realtime
    """

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        if is_token_valid(self.token):
            self.user = getUser(self.token)
            # Add current channel to user channel group
            await self.channel_layer.group_add(f"user_{self.user.user}", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Remove current channel from user channel Group
        await self.channel_layer.group_discard(f"user_{self.user.user}", self.channel_name)

    async def user_notification(self, event):
        await self.send(text_data=json.dumps(event))
