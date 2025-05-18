# consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer


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
        await self.send_json(
            {
                "type": "seat_added",
                "seat_id": event["seat_id"],
                "seat_row": event["seat_row"],
                "seat_col": event["seat_col"],
                "room": event["room"],
            }
        )

    async def booking_update(self, event):
        print("Booking update event received:", event)
        await self.send_json(
            {
                "type": "seat_update",
                "seats": event["message"]["seat_ids"],
                "booking_id": event["message"]["booking_id"],
            }
        )
