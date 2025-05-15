from django.urls import path

from .views import (check_view, create_view, exists_view, key_view, private_key_get_view, private_key_save_view,
                    secret_chats_view, status_view, user_view, user_by_name_view)

app_name = "users"

urlpatterns = [
    path("create/", create_view, name="create"),
    path("check/", check_view, name="check"),
    path("exists/", exists_view, name="exists"),
    path("status/", status_view, name="status"),
    path("user/by_name/", user_by_name_view, name="user_by_name"),
    path("user/<user_id>/", user_view, name="user"),
    path("<user_id>/secret-chats/", secret_chats_view, name="secret_chats"),
    path("<user_id>/key/", key_view, name="key"),
    path("private-key/get/", private_key_get_view, name="private-key-get"),
    path("private-key/save/", private_key_save_view, name="private-key-save"),
]
