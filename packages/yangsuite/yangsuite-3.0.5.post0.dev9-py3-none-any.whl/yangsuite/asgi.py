# mysite/asgi.py
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from yangsuite.settings.base import prefs
from yangsuite.socketio_config import sio_app

django_asgi_application = get_asgi_application()

from .urls import websocket_urlpatterns     # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", prefs.get('settings_module'))

application = ProtocolTypeRouter(
    {
        "http": URLRouter([
            path("socket.io/", sio_app),
            re_path(r'^.*$', django_asgi_application),
        ]),
        "websocket": AuthMiddlewareStack(URLRouter(
            [path("socket.io/", sio_app)] + websocket_urlpatterns
        )),
    }
)
