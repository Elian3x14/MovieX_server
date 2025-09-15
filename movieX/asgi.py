import os
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import app.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieX.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,  # HTTP requests sẽ được xử lý bởi Django bình thường
        "websocket": AuthMiddlewareStack(  # WebSocket sẽ đi qua middleware xác thực
            URLRouter(app.routing.websocket_urlpatterns)  # URL routing cho websocket
        ),
    }
)
