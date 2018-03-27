import json

# ['__cause__', '__class__', '__context__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__suppress_context__', '__traceback__', '__weakref__', 'args', 'init', 'send_to', 'with_traceback']
class ClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client.
    """
    def init(self, code):
        print("YO", dir(self))
        print("YO", self.__dir__)
        super(ClientError, self).init(code)
        self.code = code

    def send_to(self, channel):
        print("YO", dir(self))
        print("YO", self.__dir__)
        channel.send({
            "text": json.dumps({
                "error": self.code,
            }),
        })
