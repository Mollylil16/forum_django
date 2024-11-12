from django.urls import path
from forum import consumers  # Remplacez "votre_app" par le nom de votre application

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]
