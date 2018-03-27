from django.contrib import admin
from .models import Chat, Message

admin.site.register(
    Chat,
    # list_display=["id", "requester", "accepter", "pending", "accepted", "requester_learns", "requester_teaches"],
    # list_display_links=["requester", "accepter"],
    # for now, create rooms through admin, manual slugs through title
    # prepopulated_fields={"slug": ("title",)},

)

admin.site.register(Message,
    list_display=["message", "id"],)
