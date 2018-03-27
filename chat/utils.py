from channels.db import database_sync_to_async
import datetime
from functools import wraps

from .exceptions import ClientError
from .models import Chat, Message
from user_profile.models import Profile
from itertools import chain
from notifications import notify


@database_sync_to_async
def catch_client_error(func):
    """
    Decorator to catch the ClientError exception and translate it into a reply.
    """
    @wraps(func)
    def inner(message, *args, **kwargs):
        try:
            return func(message, *args, **kwargs)
        except ClientError as e:
            # If we catch a client error, tell it to send an error string
            # back to the client on their reply channel
            e.send_to(message.reply_channel)
    return inner


@database_sync_to_async
def get_room_or_error(room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    # Check if the user is logged in
    if not user.is_authenticated():
        raise ClientError("USER_HAS_TO_LOGIN")
    # Find the room they requested (by ID)
    # by id AND user, or pair.
    try:
        # room = Pair.objects.get(pk=room_id).chat_room
        # room = Pair.chat_room.get(pk=room_id)
        room = Chat.objects.get(pair__id=room_id)
    except Chat.DoesNotExist:
        raise ClientError("ROOM_INVALID")
    # Check permissions
    # if room.staff_only and not user.is_staff:
        raise ClientError("ROOM_ACCESS_DENIED")
    return room


@database_sync_to_async
def get_saved_messages(recipient, sender):
    recipient = Profile.objects.get(user__username=recipient)
    sender = Profile.objects.get(user__username=sender)
    qs_1 = Message.objects.filter(recipient=recipient, sender=sender)
    qs_2 = Message.objects.filter(recipient=sender, sender=recipient)

    all_messages = sorted(chain(qs_1, qs_2),
                          key=lambda instance: instance.timestamp)
    return all_messages


@database_sync_to_async
def get_last_ten(roomID, recipient, sender):
    recipient = Profile.objects.get(user__username=recipient)
    sender = Profile.objects.get(user__username=sender)
    qs_1 = Message.objects.filter(room=roomID, recipient=recipient, sender=sender)
    qs_2 = Message.objects.filter(room=roomID, recipient=sender, sender=recipient)

    all_messages = sorted(chain(qs_1, qs_2),
                          key=lambda instance: instance.timestamp)
    # We want to show the last 10 messages, ordered most-recent-last
    all_messages.reverse()
    chat_queryset = all_messages[:-5]
    print("ordered======", chat_queryset)
    chat_message_count = len(chat_queryset)
    print(chat_message_count)
    if chat_message_count > 0:
        first_message_id = chat_queryset[len(chat_queryset)-1].id
        print(first_message_id)
    else:
        first_message_id = -1
    previous_id = -1
    if first_message_id != -1:
        print("trying..")
        chat_room = Chat.objects.get(pair=roomID)
        try:
            previous_id = Message.objects.filter(room=chat_room, pk__lt=first_message_id).order_by("-pk")[:1][0].id
        except IndexError:
            previous_id = -1
    chat_messages = reversed(chat_queryset)
    # chat_messages = chat_queryset
    print("PREVIOUS ID IS", previous_id)

    return {
        'chat_messages': chat_messages,
        'first_message_id' : previous_id,
    }



    # for msg in all_messages:
    #     final_msg = {'room': str(room.pair.id), 'message': msg.message, 'username': msg.sender.user.username, 'msg_type': MSG_TYPE_MESSAGE}
    #     message.reply_channel.send(
    #         {"text": json.dumps(final_msg)}
    #     )


@database_sync_to_async
def save_message_object(room, sender, message, recipient):
    recipient = Profile.objects.get(user__username=recipient)
    sender = Profile.objects.get(user__username=sender)
    m = Message(room=room, sender=sender, message=message, recipient=recipient)
    m.save()
    notify.send(
            sender.user,
            recipient=recipient.user,
            verb='sent you a new message',
            timestamp=datetime.datetime.now()
        )
