from datetime import timezone, timedelta
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from threading import Thread
from channels.db import database_sync_to_async
from deployments.models import Project, Node
from users.utils.ws_auth import is_token_valid, getUser
from datetime import timedelta
import hashlib
import time
import jwt
from django.conf.global_settings import SECRET_KEY
from users.models import UserProfile


class UserSession(AsyncWebsocketConsumer):
    """
    A WebSocket comsumer that is incharge of reporting events to user in realtime
    """

    async def connect(self):
        self.token = self.scope['url_route']['kwargs']['token']
        print(f"Token ===  {self.token}")
        if await self.is_token_valid(self.token):
            user_profile = await self.getUserData(self.token)
            self.channel_group_name = f"""user_{str(user_profile["id"])}"""
            # Add current channel to user channel group
            await self.channel_layer.group_add(self.channel_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        self.token = self.scope['url_route']['kwargs']['token']
        if await self.is_token_valid(self.token):
            user_profile = await self.getUserData(self.token)
            self.channel_group_name = f"""user_{str(user_profile["id"])}"""
            await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)

    @database_sync_to_async
    def is_token_valid(self, token):
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = payload["user"]
        exp = payload["exp"]
        if UserProfile.objects.filter(user=user).exists():
            return True
        return False

    @database_sync_to_async
    def getUser(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user = payload["user"]
            if UserProfile.objects.filter(user=user).exists():
                return UserProfile.objects.get(user=user)
            return None
        except:
            return None

    @database_sync_to_async
    def getUserData(self, token):
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = payload["user"]
        userprofile = UserProfile.objects.get(user=user)
        data = {
            "id": userprofile.user.id
        }
        return data

    async def user_notification(self, event):
        print("Sending notification to user")
        print(event)
        await self.send(text_data=json.dumps(event))
