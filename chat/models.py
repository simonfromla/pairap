from django.db import models
# from channels import Group
from django.utils import timezone
from .settings import MSG_TYPE_MESSAGE
from user_profile.models import Profile, Pair
import json
from notifications.signals import notify
from datetime import datetime

# from django.contrib.auth import get_user_model

# User = get_user_model()

# Create your models here.
# from django.apps import apps


# Profile = apps.get_model('user_profile', 'Profile')

class Chat(models.Model):
    pair = models.OneToOneField(Pair, related_name='chat_room')

    # requester = models.ForeignKey('user_profile.Profile', related_name='is_requester')
    # accepter = models.ForeignKey('user_profile.Profile', related_name='is_accepter')

    # requester_learns = models.CharField(max_length=60, null=True)
    # requester_teaches = models.CharField(max_length=60, null=True)

    # pending = models.BooleanField(default=False)
    # accepted = models.BooleanField(default=False)
    # denied = models.BooleanField(default=False)

    # completed = models.BooleanField(default=False)

    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)

    @property
    def group_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return "room-%s" % self.pair.id

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("room-%s" % self.pk)

    def send_message(self, message, msg_sender_profile, recipient, msg_type=MSG_TYPE_MESSAGE):
        """
        Called to send a message to the room on behalf of a user.
        """
        # print("ONE")
        print("msg_sender type", type(msg_sender_profile))
        final_msg = {'room': str(self.pair.id), 'message': message, 'username': msg_sender_profile.user.username, 'msg_type': msg_type}
        if msg_type == MSG_TYPE_MESSAGE:
            recipient = Profile.objects.get(user__username=recipient)
            m = Message(sender=msg_sender_profile, message=message, recipient=recipient)
            m.save()

        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )
        recipient = Profile.objects.get(user__username=recipient)
        notify.send(
            msg_sender_profile.user,
            recipient=recipient.user,
            verb='sent you a new message',
            timestamp=datetime.now()
        )


# class Chat(models.Model):
#     """
#     A room for people to chat in.
#     """

#     pair = models.ForeignKey(Pair, related_name='pair_to')
#     date_started = models.DateTimeField(auto_now_add=True)
#     title = models.CharField(max_length=255)

#     @property
#     def websocket_group(self):
#         """
#         Returns the Channels Group that sockets should subscribe to to get sent
#         messages as they are generated.
#         """
#         return Group("room-%s" % self.id)

#     # def send_message(self, message, user, msg_type=MSG_TYPE_MESSAGE):
#     #     """
#     #     Called to send a message to the room on behalf of a user.
#     #     """
#     #     final_msg = {'room': str(self.id), 'message': message, 'username': user.username, 'msg_type': msg_type}

#     #     # Send out the message to everyone in the room
#     #     self.websocket_group.send(
#     #         {"text": json.dumps(final_msg)}
#     #     )


class Message(models.Model):
    room = models.ForeignKey(Chat, related_name='messages', null=True)
    recipient = models.ForeignKey(Profile, related_name='is_recipient', null=True)
    sender = models.ForeignKey(Profile, related_name='is_sender', null=True)
    message = models.TextField(null=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return str(self.message)
