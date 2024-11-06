from django.contrib import admin
from .models import UserProfile, Post, Message, Comment

admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Comment)

