import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from forum_bricoleur.routing import websocket_urlpatterns  # Remplacez "votre_projet" par le nom de votre projet

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
