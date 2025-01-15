from django.urls import path

from .views import check_view, create_view, exists_view, upload_avatar_view, user_view

app_name = "users"

urlpatterns = [
    path("create/", create_view, name="create"),
    path("check/", check_view, name="check"),
    path("exists/", exists_view, name="exists"),
    path("user/<user_id>/", user_view, name="user"),
    path("upload-avatar/", upload_avatar_view, name="upload-avatar"),
]
