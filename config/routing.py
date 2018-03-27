from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from chat.consumers import ChatConsumer, LoadHistoryConsumer


application = ProtocolTypeRouter({

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url("^chat/loadhistory/$", LoadHistoryConsumer),
            url("^chat/stream/$", ChatConsumer),
        ])
    ),
})
