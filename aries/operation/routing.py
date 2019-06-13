from channels import route

from aries.operation import consumers

channel_routing = [
    route('websocket.disconnect', consumers.on_disconnect),
    route('websocket.receive', consumers.message_handler),
    route('websocket.keepalive', consumers.keep_alive_message),
    route('websocket.connect', consumers.on_connect),
]
