import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PayrollSyncConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We'll use a generic group for all updates
        self.group_name = 'payroll_updates'

        # Join the updates group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the updates group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from room group
    async def data_update(self, event):
        # Forward the entire event payload except the 'type' which is standard
        payload = {k: v for k, v in event.items() if k != 'type'}
        payload['type'] = 'update'

        # Send message to WebSocket
        await self.send(text_data=json.dumps(payload))
