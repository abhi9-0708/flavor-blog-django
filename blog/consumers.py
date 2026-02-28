import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_slug = self.scope['url_route']['kwargs']['post_slug']
        self.room_group_name = f'comments_{self.post_slug}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # This method receives messages from the group and sends them to the client
    async def comment_message(self, event):
        comment = event['comment']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'comment': comment
        }))