from django.urls import path

from .views import (check_view, count_auth_view, create_view, exists_view, key_view, secret_chats_view, status_view,
                    user_view)

app_name = "users"

urlpatterns = [
    path("create/", create_view, name="create"),
    path("check/", check_view, name="check"),
    path("exists/", exists_view, name="exists"),
    path("status/", status_view, name="status"),
    path("user/<user_id>/", user_view, name="user"),
    path("<user_id>/secret-chats/", secret_chats_view, name="secret_chats"),
    path("<user_id>/key/", key_view, name="key"),
    path("count-auth/", count_auth_view, name="count-auth"),
]
