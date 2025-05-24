from django.urls import path

from .views import (chat_view, chats_view, create_chat_view, create_secret_chat_view, delete_chat_view,
                    get_chat_users_view, message_view, messages_view)

app_name = "chats"

urlpatterns = [
    path("", chats_view, name="chats"),
    path("secret-chat/create/", create_secret_chat_view, name="create_secret_chat"),
    path("chat/create/", create_chat_view, name="create_chat"),
    path("chat/<chat_id>/", chat_view, name="chat"),
    path("<chat_id>/users/", get_chat_users_view, name="get_chat_users"),
    path("<dialog_id>/messages/", messages_view, name="messages"),
    path("<dialog_id>/message/", message_view, name="message"),
    path("<chat_id>/", delete_chat_view, name="delete_chat"),
]
