import json
# from channels import Channel
# from channels.auth import channel_session_user_from_http, channel_session_user
from channels.generic.websocket import AsyncJsonWebsocketConsumer, JsonWebsocketConsumer

from .settings import (
    MSG_TYPE_LEAVE,
    MSG_TYPE_ENTER,
    MSG_TYPE_MESSAGE,
    NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS
)
# from .models import Room
from .models import Chat, Message
from user_profile.models import Profile, Pair
from .utils import (get_room_or_error,
                    catch_client_error,
                    get_saved_messages,
                    save_message_object,
                    get_last_ten,)
from .exceptions import ClientError

# from django.contrib.auth import get_user_model

from itertools import chain

### WebSocket handling ###

# profile = get_user_model()

# This decorator copies the user from the HTTP session (only available in
# websocket.connect or http.request messages) to the channel session (available
# in all consumers with the same reply_channel, so all three here)

class LoadHistoryConsumer(JsonWebsocketConsumer):

    def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            self.close()
        else:
            # Accept the connection
            self.accept()
        # Store which rooms the user has joined on this connection
        self.rooms = set()

    def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        print("HIST CONTENT", content)
        sender = self.scope["user"]
        room = json.loads(content['room'])
        last_message_id = json.loads(content['last_message_id'])
        print(room, last_message_id)
        chat_queryset = Message.objects.filter(room=room, id__lte=last_message_id).order_by("-timestamp")[:10]
        chat_message_count = len(chat_queryset)
        if chat_message_count > 0:
            first_message_id = chat_queryset[len(chat_queryset)-1].id
        else:
            first_message_id = -1
        previous_id = -1
        if first_message_id != -1:
            try:
                previous_id = Message.objects.filter(room=room, pk__lt=first_message_id).order_by("-pk")[:1][0].id
            except IndexError:
                previous_id = -1

        chat_messages = reversed(chat_queryset)
        cleaned_chat_messages = list()
        for item in chat_messages:
            current_message = item.message
            cleaned_item = {'username': item.sender.user.username, 'message': current_message}
            cleaned_chat_messages.append(cleaned_item)

        # my_dict = { 'messages' : cleaned_chat_messages, 'previous_id' : previous_id }
        # message.reply_channel.send({'text': json.dumps(my_dict)})
        # for msg in cleaned_chat_messages:
        self.send_json({
            "msg_type": MSG_TYPE_MESSAGE,
            "room": room,
            "messages": cleaned_chat_messages,
            "previous_id": previous_id,
        },)
        # self.send_json({
        #     "previous_id": previous_id
        #     })





        # Messages will have a "command" key we can switch on
        # command = content.get("command", None)
        # recipient = content.get("recipient", None)
        # sender = self.scope["user"]
        # try:
        #     if command == "join":
        #         print("JOINED receive json")
        #         # Make them join the room
        #         await self.join_room(content["room"])
        #         previous_message_list = await get_saved_messages(recipient, sender)
        #         for msg in previous_message_list:
        #             await self.send_json({
        #                 "msg_type": MSG_TYPE_MESSAGE,
        #                 "room": content["room"],
        #                 "username": msg.sender.user.username,
        #                 "message": msg.message,
        #             },)
        #     elif command == "leave":
        #         print("LEAVE receive json")
        #         # Leave the room
        #         await self.leave_room(content["room"])
        #     elif command == "send":
        #         print("SEND receive json")
        #         print(content)
        #         await self.send_room(
        #             content["room"],
        #             content["message"],
        #             content["recipient"]
        #         )
        # except ClientError as e:
        #     # Catch any errors and send it back
        #     await self.send_json({"error": e.code})

    async def disconnect(self, code):
        pass


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    This chat consumer handles websocket connections for chat clients.

    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html
    """

    ##### WebSocket event handlers

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
        # Store which rooms the user has joined on this connection
        self.rooms = set()

    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        command = content.get("command", None)
        recipient = content.get("recipient", None)
        sender = self.scope["user"]
        try:
            if command == "join":
                print("JOINED receive json")
                # Make them join the room
                await self.join_room(content["room"])
                # previous_message_list = await get_saved_messages(recipient, sender)
                previous_message_and_first_id = await get_last_ten(content['room'], recipient, sender)
                for msg in previous_message_and_first_id["chat_messages"]:
                    await self.send_json({
                        "msg_type": MSG_TYPE_MESSAGE,
                        "room": content["room"],
                        "username": msg.sender.user.username,
                        "message": msg.message,
                    },)
                await self.send_json({
                    "first_message_id": previous_message_and_first_id["first_message_id"]
                    })

                print("++++" ,previous_message_and_first_id["first_message_id"])


            elif command == "leave":
                print("LEAVE receive json")
                # Leave the room
                await self.leave_room(content["room"])
            elif command == "send":
                print("SEND receive json")
                print(content)
                await self.send_room(
                    content["room"],
                    content["message"],
                    content["recipient"]
                )
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        for room_id in list(self.rooms):
            try:
                await self.leave_room(room_id)
            except ClientError:
                pass

    ##### Command helper methods called by receive_json

    async def join_room(self, room_id):
        """
        Called by receive_json when someone sent a join command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        room = await get_room_or_error(room_id, self.scope["user"])
        # Send a join message if it's turned on
        if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.join",
                    "room_id": room_id,
                    "username": self.scope["user"].username,
                }
            )
        # Store that we're in the room
        self.rooms.add(room_id)
        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish opening the room
        await self.send_json({
            "join": str(room.pair.id),
            # "title": room.title,
        })

    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        room = await get_room_or_error(room_id, self.scope["user"])
        # Send a leave message if it's turned on
        if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.leave",
                    "room_id": room_id,
                    "username": self.scope["user"].username,
                }
            )
        # Remove that we're in the room
        self.rooms.discard(room_id)
        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish closing the room
        await self.send_json({
            "leave": str(room.pair.id),
        })

    async def send_room(self, room_id, message, recipient):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        if room_id not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED")
        # Get the room and send to the group about it
        room = await get_room_or_error(room_id, self.scope["user"])
        print("555555")
        await save_message_object(
            room=room,
            sender=self.scope["user"].username,
            message=message,
            recipient=recipient
        )
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "room_id": room_id,
                "username": self.scope["user"].username,
                "message": message,
                "recipient": recipient,
            }
        )

    ##### Handlers for messages sent over the channel layer

    # These helper methods are named by the types we send - so chat.join becomes chat_join
    async def chat_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": MSG_TYPE_ENTER,
                "room": event["room_id"],
                "username": event["username"],
            },
        )

    async def chat_leave(self, event):
        """
        Called when someone has left our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": MSG_TYPE_LEAVE,
                "room": event["room_id"],
                "username": event["username"],
            },
        )

    async def chat_message(self, event):
        print("===",event)
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        # Save message object
        # await save_message_object(
        #     sender=event["username"],
        #     message=event["message"],
        #     recipient=event["recipient"]
        # )
        await self.send_json(
            {
                "msg_type": MSG_TYPE_MESSAGE,
                "room": event["room_id"],
                "username": event["username"],
                "message": event["message"],
            },
        )
