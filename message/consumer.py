import json
import base64
from django.core.files.base import ContentFile
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from authentication.models import User
from message.models import Thread, ChatMessage
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from uuid import uuid4
from asgiref.sync import sync_to_async
from helper.slack_logger import send_error_to_slack as logs


# converting base64 to imagefield
def base64_to_image(base64_string):
    format, imgstr = base64_string.split(";base64,")
    ext = format.split("/")[-1]
    return ContentFile(base64.b64decode(imgstr), name=uuid4().hex + "." + ext)


# create a consumer that handles WebSocket connections
class ChatConsumer(AsyncConsumer):
    # handle WebSocket connections
    async def websocket_connect(self, event):
        # Get the thread ID from the URL parameters
        thread_id = self.scope["url_route"]["kwargs"]["thread_id"]

        # extract the token from the headers
        headers = dict(self.scope["headers"])
        token_key = headers.get(b"authorization", b"").decode("utf-8").split()[1]

        # authenticate the user using the token
        user = await self.get_user_from_token(token_key)

        # accept the WebSocket connection
        await self.send({"type": "websocket.accept"})

        if isinstance(user, AnonymousUser):
            # If the user is an AnonymousUser, it means the token is invalid
            # Send an custom code to the client for verification
            await self.send(
                {
                    "type": "websocket.send",
                    "text": json.dumps({"error": "User is not authorized"}),
                }
            )
            await self.send({"type": "websocket.close", "code": 3000})
            return

        # set the authenticated user in the scope
        self.scope["user"] = user

        # Check if the thread belongs to the user
        thread = await self.get_thread(thread_id)
        if await sync_to_async(
            lambda: thread is None or not (thread.user1 == user or thread.user2 == user)
        )():
            # Send an error message to the client for an invalid thread_id
            await self.send(
                {
                    "type": "websocket.send",
                    "text": json.dumps({"error": "Invalid thread_id"}),
                }
            )
            await self.send({"type": "websocket.close", "code": 4000})
            return

        # create a chat room name based on the user's ID
        chat_room = f"user_chatroom_{user.id}"

        # store the chat room name for later use
        self.chat_room = chat_room

        # add the client's channel to the chat room group
        await self.channel_layer.group_add(chat_room, self.channel_name)

        # Update user's online status to True
        await self.update_user_online_status(user, True, thread_id)

        # Get all unread messages for the user in the thread
        unread_messages = await self.get_all_unread_messages(user, thread_id)

        # Send the unread message data to the client
        response = {
            "type": "unread_messages",
            "messages": unread_messages,
        }
        await self.channel_layer.group_send(
            self.chat_room, {"type": "chat_message", "text": json.dumps(response)}
        )

        # Mark all messages as read for the user
        await self.mark_all_messages_as_read(user, thread_id)

    # handle WebSocket disconnections
    async def websocket_disconnect(self, event):
        # extract the token from the headers
        headers = dict(self.scope["headers"])
        token_key = headers.get(b"authorization", b"").decode("utf-8").split()[1]

        # authenticate the user using the token
        user = await self.get_user_from_token(token_key)
        # Update user's online status to False
        await self.update_user_online_status(user, False)

    async def websocket_receive(self, event):
        # extract message data from the event
        text_data = event.get("text")
        message_data = json.loads(text_data)

        # extract individual fields from the message data
        message = message_data.get("message")
        image_data = message_data.get("image")

        # get the authenticated user as the sender
        sent_by_user = self.scope["user"]
        sent_by_user = sent_by_user.id

        # fetch the thread ID from the URL
        thread_id = self.scope["url_route"]["kwargs"].get("thread_id")

        # check for errors in the message data
        if not message and not image_data:
            # Send an error message to the client
            await self.send(
                {
                    "type": "websocket.send",
                    "text": json.dumps({"error": "Message or image data is missing"}),
                }
            )
            return

        # authenticate the sender and receiver
        sent_by_user = await self.get_user_object(sent_by_user)

        # retrieve the thread object and validate
        thread_obj = await self.get_thread(thread_id)
        if await sync_to_async(
            lambda: thread_obj is None
            or not (
                thread_obj.user1 == sent_by_user or thread_obj.user2 == sent_by_user
            )
        )():
            # Send an error message to the client for invalid thread_id
            await self.send(
                {
                    "type": "websocket.send",
                    "text": json.dumps({"error": "Invalid thread_id"}),
                }
            )
            await self.send({"type": "websocket.close", "code": 4000})
            return

        # fetch the recipient's ID from the thread
        send_to_id = await sync_to_async(
            lambda: thread_obj.user2.id
            if thread_obj.user1_id == sent_by_user.id
            else thread_obj.user1.id
        )()

        print(send_to_id)

        # authenticate the recipient
        send_to_user = await self.get_user_object(send_to_id)

        # Convert the base64 image to ImageField and assign it to the profile_picture field
        if image_data:
            try:
                message_image = image_data
                image = base64_to_image(message_image)
            except Exception as e:
                # Send an error message to the client
                await self.send(
                    {
                        "type": "websocket.send",
                        "text": json.dumps(
                            {"error": f"Error while saving the image {str(e)}"}
                        ),
                    }
                )
                return
        else:
            image = None

        # create a ChatMessage object from the message data
        # Check if either message or image is present
        chat_message = None
        if message or image:
            # Create a ChatMessage object from the message data and save it
            chat_message = await self.create_chat_message(
                thread_obj, sent_by_user, message
            )
            if chat_message:
                if image is not None:
                    chat_message.image = image
                await sync_to_async(chat_message.save)()

        # create a response object to send to the recipient
        other_user_chat_room = f"user_chatroom_{send_to_id}"

        # Construct the response message data
        response = {
            "type": "message",
            "message": chat_message.message if chat_message else None,
            "image": chat_message.image.url
            if chat_message and chat_message.image
            else None,
            "sender": {
                "id": sent_by_user.id,
                "username": sent_by_user.username,
            },
            "timestamp": chat_message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if chat_message
            else None,
        }

        # Check if the recipient is online
        if send_to_user.online and send_to_user.current_thread_id == thread_id:
            # Set the 'is_read' status to True if the recipient is online
            response["is_read"] = True
            # send the response to the recipient's chat room
            await self.channel_layer.group_send(
                other_user_chat_room,
                {"type": "chat_message", "text": json.dumps(response)},
            )
        else:
            # Set the 'is_read' status to False if the recipient is offline
            response["is_read"] = False

        # send the response to the sender's chat room
        await self.channel_layer.group_send(
            self.chat_room, {"type": "chat_message", "text": json.dumps(response)}
        )

        # mark the chat message as read by the recipient
        if send_to_user.online and send_to_user.current_thread_id == thread_id:
            await self.mark_message_as_read(chat_message)

    @database_sync_to_async
    def get_user_object(self, user_id):
        """
        This function queries the database to retrieve a User object based on a user_id.
        It is wrapped with database_sync_to_async so it can be called asynchronously.
        It returns a User object if it exists, otherwise it returns None
        """
        try:
            qs = User.objects.get(id=user_id)
            return qs
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_thread(self, thread_id):
        """
        This function queries the database to retrieve a Thread object based on a thread_id.
        It is wrapped with database_sync_to_async so it can be called asynchronously.
        It returns a Thread object if it exists, otherwise it returns None.
        """
        try:
            thread = Thread.objects.get(id=thread_id)
            return thread
        except Thread.DoesNotExist:
            return None

    @database_sync_to_async
    def update_user_online_status(self, user, is_online, thread_id=None):
        """
        Update the online status of a user.
        """
        try:
            user_status = User.objects.get(username=user)
            user_status.current_thread_id = thread_id
            user_status.online = is_online
            user_status.save()
        except User.DoesNotExist:
            pass

    @database_sync_to_async
    def create_chat_message(self, thread, user, message):
        """
        This function creates a new ChatMessage object with an image and saves it to the database.
        It is wrapped with database_sync_to_async so it can be called asynchronously.
        It takes a Thread object, a User object, a message string, and an image file as arguments.
        """
        chat_message = ChatMessage.objects.create(
            thread=thread, sender=user, message=message
        )
        return chat_message

    @database_sync_to_async
    def mark_message_as_read(self, chat_message):
        """
        This function marks a ChatMessage as read by the recipient.
        It is wrapped with database_sync_to_async so it can be called asynchronously.
        It takes a ChatMessage object and a User object as arguments.
        """
        chat_message.is_read = True
        chat_message.save()
        return True

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        """
        This function retrieves a User object based on a token key.
        It is wrapped with database_sync_to_async to make it asynchronous.
        It returns the User object if it exists, otherwise it returns an AnonymousUser.
        """
        try:
            token = Token.objects.get(key=token_key)
            user = token.user
        except Token.DoesNotExist:
            user = AnonymousUser()
        return user

    async def chat_message(self, event):
        # Handle chat messages
        text = event["text"]
        # Process the chat message and perform necessary actions
        # For example, you can send the message to the connected WebSocket client
        await self.send(
            {
                "type": "websocket.send",
                "text": text,
            }
        )

    @database_sync_to_async
    def get_all_unread_messages(self, user, thread_id):
        """
        Get all unread messages of user in a thread.
        """
        try:
            thread = Thread.objects.get(id=thread_id)
            # Get all chat messages in the thread that are unread by the user
            unread_messages = ChatMessage.objects.filter(
                thread=thread, is_read=False
            ).exclude(sender=user)
            # Create a list to hold the serialized message data
            messages_data = []
            # Iterate over the unread messages and extract the desired data
            for message in unread_messages:
                message_data = {
                    "id": message.id,
                    "message": message.message,
                    "image": message.image.url if message.image else None,
                    "sender": {
                        "id": message.sender.id,
                        "username": message.sender.username,
                    },
                    "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_read": message.is_read,
                }
                messages_data.append(message_data)
            return messages_data
        except Thread.DoesNotExist:
            # Handle the case when the thread does not exist
            return []

    @database_sync_to_async
    def mark_all_messages_as_read(self, user, thread_id):
        """
        Mark all messages as read for the given user when the recipient is online.
        """
        try:
            thread = Thread.objects.get(id=thread_id)
            recipient = thread.user1 if thread.user2 == user else thread.user2

            # Update is_read to True if recipient is online or sender is offline
            if recipient.online and not user.online:
                ChatMessage.objects.filter(thread=thread).update(is_read=True)
        except Thread.DoesNotExist:
            pass
