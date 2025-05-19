# consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json


class BookingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope["url_route"]["kwargs"]["booking_id"]
        self.group_name = f"booking_{self.booking_id}"
        print(f"Group name: {self.group_name}")
        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def seat_added(self, event):
        # TODO: Thêm log ở đây 
        message = event["message"]
        await self.send(
            json.dumps(
                {
                    "type": "seat_added",
                    "seat_id": message["seat_id"],  # lấy từ event["message"]
                }
            )
        )

    async def seat_removed(self, event):
        message = event["message"]
        await self.send_json(
            json.dumps(
                {
                    "type": "seat_removed",
                    "seat_id": message["seat_id"],
                }
            )
        )
