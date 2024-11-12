# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CustomLoginView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    register,
    post_list,
    post_create,
    post_detail,
    send_message,
    ProfileView,
    password_change,
    inbox,
    delete_comment,
    view_message,
    toggle_follow,
    like_post,
    dislike_post,
    chat_room,
)

urlpatterns = [
    path('', post_list, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('inbox/', inbox, name='inbox'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('register/', register, name='register'),
    path('post/create/', post_create, name='post_create'),
    path('post/<int:pk>/', post_detail, name='post_detail'),
    path('send_message/<int:recipient_id>/', send_message, name='send_message'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'),  # Ajout de l'argument user_id
    path('password_change/', password_change, name='password_change'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('message/<int:message_id>/', view_message, name='view_message'),
    path('follow/<int:user_id>/', toggle_follow, name='toggle_follow'),
    path('post/<int:post_id>/like/', like_post, name='like_post'),
    path('post/<int:post_id>/dislike/', dislike_post, name='dislike_post'),
    path('<str:room_name>/', chat_room, name='chat_room'),
    
]
