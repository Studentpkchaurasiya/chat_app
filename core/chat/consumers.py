
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  
django.setup()


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Message

clients = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.username = None

    async def receive(self, text_data):
        data = json.loads(text_data)

        # First message = register username
        if self.username is None:
            self.username = data.get("username")
            if not self.username:
                await self.send(json.dumps({
                    "from": "server",
                    "message": " Send your username first"
                }))
                return
            clients[self.username] = self
            await self.send(json.dumps({
                "from": "server",
                "message": f" Registered as {self.username}"
            }))
            return

        # Handle chat messages
        to_user = data.get("to")
        message = data.get("message")
        if not to_user or not message:
            await self.send(json.dumps({
                "from": "server",
                "message": " Invalid format, use {to:'username', message:'...'}"
            }))
            return

        # Save message in DB
        await self.save_message(self.username, to_user, message)

        # Deliver to recipient if connected
        recipient = clients.get(to_user)
        if recipient:
            await recipient.send(json.dumps({
                "from": self.username,
                "message": message
            }))
        else:
            await self.send(json.dumps({
                "from": "server",
                "message": f" User {to_user} not connected"
            }))

    async def disconnect(self, close_code):
        if self.username in clients:
            del clients[self.username]

    @sync_to_async
    def save_message(self, sender_username, receiver_username, text):
        try:
            sender = User.objects.get(username=sender_username)
            receiver = User.objects.get(username=receiver_username)
            Message.objects.create(sender=sender, receiver=receiver, text=text)
        except User.DoesNotExist:
            pass
